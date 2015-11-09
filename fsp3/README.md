# Catalog Application

## Overview

Create, read, update and delete catalog items.

Items can only be added by users that have logged in using google+ or facebook login.

Items can only be edited and deleted by the user that created the item.

This application uses the python microframework Flask.


## Requirements

This application was developed and tested with Python 2.7.6 on a Windows 10 machine using virtualbox and vagrant.
The following directions assume you have virtualbox and vagrant installed and are using a Windows 10 machine. 

## Usage

In git bash:

    git clone https://github.com/rozisaacson/fsp3.git
    cd /vagrant
    vagrant up
    vagrant ssh
    cd /vagrant
    sudo pip install werkzeug==0.8.3
    sudo pip install flask==0.9
    sudo pip install Flask-Login==0.1.3
    sudo pip install Flask-Bootstrap--3.3.5.7
    sudo pip install Flask-wtf==0.1.2
    cd fsp3
    python catalog_db_setup.py
    python populate.py
    python app.py

Then, in a browser, go to localhost:5000

A JSON endpoint is available at localhost:5000/catalog/api

## Attribution ##

Full Stack Foundations and OAuth Udacity Courses and Discussion Board
Miguel Grinberg's excellent Flask Tutorials
 



