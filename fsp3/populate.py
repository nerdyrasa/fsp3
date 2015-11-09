from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Test", email="test",
             picture='test.jpg', id=1)
session.add(User1)

session.commit()


# Categories
cat1 = Category(id=1, name="Laptops",
                description="A laptop combines the components and inputs of a desktop computer, including the display, speakers, a keyboard, and pointing devices (such as a touchpad or trackpad) into a single one. Most modern-day laptops also have integrated webcams and built-in microphones. This device can be powered either from a rechargeable battery or from an AC adapter.",
                image="laptop.png", user_id=1)
session.add(cat1)

cat2 = Category(id=2, name="Desktops",
                description="A desktop computer is a personal computer in a form intended for regular use at a single location desk/table due to its size and power requirements, as opposed to a laptop whose rechargeable battery and compact dimensions allow it to be regularly carried and used in different locations.",
                image="desktop.png", user_id=1)
session.add(cat2)

cat3 = Category(id=3, name="Tablets",
                description="A tablet computer, commonly shortened to tablet, is a mobile computer with a rectangular touchscreen display, circuitry, and battery in a single device. Tablets come equipped with sensors, including cameras, a microphone, and an accelerometer, and the touchscreen display uses the recognition of finger or stylus gestures replacing the usage of the mouse and keyboard.",
                image="tablet.jpg", user_id=1)
session.add(cat3)

session.commit()

# Category items
item1 = CategoryItem(
    name="Acer - 11.6\" Chromebook - Intel Celeron - 2GB Memory - 16GB eMMC Flash Memory - Moonstone White",
    description="Acer CB3-111-C8UB Chromebook: Great for commuters and students, this lightweight Chromebook is optimized for Web-based apps and cloud storage on the go. The antiglare screen, quick Wi-Fi capability, and quiet fanless design allow for unobtrusive productivity at coffee shops, parks and more.",
    image="laptop1.jpg",
    category_id=1,
    user_id=1)

session.add(item1)
item2 = CategoryItem(user_id=1,
                     name="Amazon - Fire HD 8 - 8\" Tablet 8GB - Blue",
                     description="Fire OS 58\" IPS touch-screen display with 1280 x 800 resolution8GB storage capacityQuad-core processorWi-FiAmazon Underground",
                     image="tablet1.jpg",
                     category_id=3)

session.add(item2)

item3 = CategoryItem(user_id=1,
                     name="Dell - Inspiron Desktop - Intel Celeron - 2GB Memory - 32GB Solid State Drive - Black",
                     description="Windows 8.1, upgrade to Windows 10 for freeTechnical details: Intel Celeron; processor; 2GB memory; 32GB solid state driveSpecial features: Built-in wireless networking; Bluetooth; HDMI output; wireless keyboard and mouseDVD/CD drive not included",
                     image="desktop1.jpg",
                     category_id=2)

session.add(item3)

item4 = CategoryItem(user_id=1,
                     name="Lenovo - Refurbished ThinkCentre Desktop - Intel Core2 Duo - 3GB Memory - 120GB Hard Drive - Black",
                     description="With a 120GB hard drive and DVD drive, this Lenovo ThinkCentre M57 TW-2.3-W7P desktop makes it easy to enjoy your favorite media. Intel Core2 Duo processor provides advanced dual-core multitasking with breakthrough power efficiency.    This product has been refurbished. ",
                     image="desktop4.jpg",
                     category_id=2)

session.add(item4)

item5 = CategoryItem(user_id=1,
                     name="HP - Refurbished Desktop - Intel Core2 Duo - 4GB Memory - 500GB Hard Drive - Gray/Black",
                     description="This HP dc5800 sff-2.3-4gb-500gb-w7p desktop provides a 500GB hard drive to store your personal and professional files. Intel Core2 Duo processor provides advanced dual-core multitasking with breakthrough power efficiency.    This product has been refurbished.",
                     image="desktop5.jpg",
                     category_id=2)

session.add(item5)

session.commit()

print("Catalog database populated! Success!")
