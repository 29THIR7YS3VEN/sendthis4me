# Sendthis4me - A web application helping you to find someone to deliver your parcel, built with HTML, Flask, Jinja, and SQL. Made for the CS50x Final Project
Sendthis4me is a web application to help people quickly and conveniently find someone to deliver your parcel, or to provide an opportunity to make money for those who are always on the go. It includes an admin dashboard to filter dispatchers (those who do the sending), as well as a tracking system that provides the senders (those who need the sending) with all the information they need.

## Usage Breif
### Admins
- The default admin account has username of DEFAULT_ADMIN and a password of DEFAULT_ADMIN_PASSWORD - this account is for initializing and testing purposes only
- New admins can be registered when a user is already logged in as an admin
- Admins can veiw all the information as inputted by each dispatcher, and activate their accounts
### Senders
- The sender dashboard displays Unconfirmed (draft) orders, current orders, and successfull orders
- The sender can create a new order by navigating to the corresponding link on their navbar, and filling in the details prompted.
- The order is then marked as a draft and remains in the unconfirmed section until confirmed.
- When confirmed, the order moves to "current orders"

### Dispatchers
- Upon registering, the dispatcher is unable to login untill their account is verified by an admin
- Once they log in, their dashboard will display Inprogress, Available for Accepting, and Completed
- Dispatchers can accept an order from the Available for Accepting section. When it moves to the Inprogress section, they can update its status per the below
### Status
- Draft: order has not been placed yet.
- Awaiting Acceptance: waiting for a dispatcher to accept the order
- On way to pickup: Dispatcher is on their way to pickup the package from the sender
- At pickup location: Dispatcher has arrived to pickup the package from the sender
- On way: Dispatcher is on the way to the specified receiver address
- At receiver address: Dispatcher has arrived at specified receiver address
- Successful: Dispatcher has successfully completed the order

## Dependencies:
- SQLalchemy
- Flask
- Flask-session
- Werkzeug
- CS50 Library for Python

## Technical Overview:
Almost the entirety of the app's functionality is contained within `app.py`, a single python file that works as the brain of the application, handling everything from registering users and logging them in to creating new orders and updating its status. `app_database_init.py` is a short python file with the main purpose being to initialize the database, taking commands from `database_schema.sql` and executing them on `database.db`, which becomes the database holding all of the app's data. Basic javascript was used for form validation, and HTML was used with Jinja templating language for the front-end, styled by CSS and Bootstrap.

## How to run (windows command promt, Python 3)
```
//create virtual enviroment
py -3 -m venv .venv
.venv\scripts\activate
```
```
//Install dependencies
pip install -r requirements.txt
```
```
//Run the application
commands\run
```
