from __future__ import print_function
import imghdr
import json
import os
import random
import string
from flask import Flask, render_template, flash, url_for, redirect, request, g, jsonify
from flask.ext.bootstrap import Bootstrap
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask.ext.wtf import Form
from wtforms import FileField, SubmitField, StringField, TextAreaField, ValidationError
from catalog_db_setup import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

bootstrap = Bootstrap(app)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


class CatalogItemForm(Form):
    name = StringField('Name')
    description = TextAreaField('Description')
    image = FileField('Image file')
    submit = SubmitField('Submit')

    def validate_image_file(self, field):
        if len(field.data.filename) != 0:
            if field.data.filename[-4:].lower() != '.jpg' and field.data.filename[-4:].lower() != '.png':
                raise ValidationError('Invalid file extension: please select a jpg or png file')

            if imghdr.what(field.data) != 'jpeg' and imghdr.what(field.data) != 'png':
                raise ValidationError('Invalid image format: please select a jpg or png file')


@app.before_request
def load_user():
    if "username" in login_session:
        print (login_session["username"])
        name = login_session["username"]
        user_id = login_session["user_id"]
        if "gplus_id" in login_session:
            gplus = True
        else:
            gplus = False
    else:
        print ("this key not in login session")
        name = None
        gplus = None
        user_id = None

    g.name = name
    g.gplus = gplus
    g.user_id = user_id



@app.route('/')
def show_categories():
    categories = session.query(Category).order_by(asc(Category.name))
    '''
    if "username" in login_session:
        print (login_session["username"])
        name = login_session["username"]
        if "gplus_id" in login_session:
            gplus = True
        else:
            gplus = False
    else:
        print ("this key not in login session")
        name = None
        gplus = None
    '''
    print('g.name = {} '.format(g.name))
    #return render_template('index.html', categories=categories, name=g.name, gplus=g.gplus)
    return render_template('index.html', categories=categories)


@app.route('/items/<int:category_id>')
def items(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id=category_id)
    return render_template('items.html', items=items, category=category)


@app.route('/item/<int:item_id>')
def show_item(item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return render_template('details.html', item=item)


@app.route('/new/item/<int:category_id>', methods=['GET', 'POST'])
def new_item(category_id):

    if (not g.user_id):
        return redirect(url_for('showLogin'))

    category = session.query(Category).filter_by(id=category_id).one()


    form = CatalogItemForm()

    if form.validate_on_submit():
        if form.image.data.filename:
            filename = form.image.data.filename
            item_image = 'images/' + filename
            form.image.data.save(os.path.join(app.static_folder, item_image))
        else:
            filename = 'no-image.png'

        new_item = CategoryItem(
            name=form.name.data,
            description=form.description.data,
            image=filename,
            category_id=category_id,
            user_id=g.user_id
        )
        session.add(new_item)
        session.commit()
        flash('New Item {} Successfully Created'.format(new_item.name))
        return redirect(url_for('show_categories'))

    return render_template('newitem.html', form=form, category_name=category.name)


@app.route('/edit/item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):

    edited_item = session.query(CategoryItem).filter_by(id=item_id).one()

    if (g.user_id != edited_item.user_id):
        return redirect(url_for('showLogin'))

    form = CatalogItemForm(obj=edited_item)

    if form.validate_on_submit():
        if form.name.data:
            edited_item.name = form.name.data
        if form.description.data:
            edited_item.description = form.description.data
        if form.image.data.filename:
            filename = form.image.data.filename
            edited_item.image = filename
            item_image = 'images/' + filename
            form.image.data.save(os.path.join(app.static_folder, item_image))
        session.add(edited_item)
        session.commit()
        flash('Item successfully edited: {}'.format(edited_item.name))
        return redirect(url_for('show_categories'))

    return render_template('edititem.html', form=form, image=edited_item.image)


@app.route('/delete/item/<int:item_id>', methods=['GET', 'POST'])
def delete_item(item_id):
    item_to_delete = session.query(CategoryItem).filter_by(id=item_id).one()
    if (g.user_id != item_to_delete.user_id):
        return redirect(url_for('showLogin'))

    form = Form()
    if request.method=='POST':
        session.delete(item_to_delete)
        name = item_to_delete.name
        session.commit()
        flash('Item successfully deleted:{}'.format(name))
        return redirect(url_for('show_categories'))
    else:
        print('delete')

        return render_template('deleteitem.html', form=form, name=item_to_delete.name)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    # state = ''.join(random.choice(string.ascii_uppercase + string.digits)
    #                for x in xrange(32))
    state = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token

    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']


    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials

    login_session['gplus_id'] = gplus_id
    print ('login credentials = {}'.format(login_session['credentials']))
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if a user exists; if it doesn't create a new one
    user_id = getUserID(login_session['email'])

    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])

    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    print("gdisconnect")
    credentials = login_session.get('credentials')

    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print("result is {}".format(result))
    if result['status'] == '200':
        # Reset the user's sesson.
        reset_user_session(login_session)
        '''
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        '''

        successful_disconnect()
        return redirect(url_for('show_categories'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#helper
def reset_user_session(my_dict):


    for key in my_dict.keys():
        print ('deleting {}: {}'.format(key, my_dict[key]))
        del my_dict[key]

    '''
    del user_session['credentials']
    del user_session['gplus_id']
    del user_session['username']
    del user_session['email']
    del user_session['picture']
    '''


def successful_disconnect():
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    flash("Successfully logged out")


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    print ("fbconnect")
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print ("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    print ("id {}".format(app_id))
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)

    h = httplib2.Http()

    result = h.request(url, 'GET')[1]
    print ('result {}'.format(result))
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print ("url sent for API access:%s"% url)
    print ("API JSON result: %s" % result)
    data = json.loads(result)

    login_session['username'] = data["name"]

    # My facebook login is with my mobile phone so my email is empty
    # This is a temporary workaround for the case when email is empty
    if 'email' in data:
        login_session['email'] = data["email"]
    else:
        login_session['email'] = 'roz.isaacson@gmail.com'

    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    print ('result = {}'.format(result))
    reset_user_session(login_session)

    successful_disconnect()
    #flash("Successfully logged out")
    return redirect(url_for('show_categories'))


@app.route('/catalog/api')
def catalog_api():
    items = session.query(CategoryItem).all()
    return jsonify(items = [i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
