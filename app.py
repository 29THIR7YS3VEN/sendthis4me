from atexit import register
from contextlib import nullcontext
from distutils.log import error
import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from datetime import datetime
from flask_mail import Mail, Message
import random
from dotenv import load_dotenv 

app = Flask(__name__)

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config['MAIL_SERVER']= 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '0a61b7f4f7d142'
app.config['MAIL_PASSWORD'] = '9b96ccbd6ad93a'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

mail = Mail(app)
Session(app)

db = SQL("sqlite:///database.db")

adminstotal = db.execute("SELECT * FROM admins")
if len(adminstotal) == 0:
    db.execute("INSERT INTO admins (username, password_hash) VALUES (:username, :password)", username="DEFAULT_ADMIN", password=generate_password_hash("DEFAULT_ADMIN"))


# HOMEPAGE =====================================================================================================
@app.route("/")
def index():
        return render_template("index.html")
# SIGNIN   =====================================================================================================
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    else:
        input_username = request.form.get("username")
        input_password = request.form.get("password")

        # check if the person signing in is an admin
        rowsadmins = db.execute("SELECT * FROM admins WHERE username = :username", username = input_username)
        if len(rowsadmins) == 1 and check_password_hash(rowsadmins[0]["password_hash"], input_password):
            session["user_id"] = rowsadmins[0]["id"]
            session["role"] = "admin"
            return redirect("/admin-dashboard")
        else:
            # check if the person signing in is a sender
            rowssenders = db.execute("SELECT * FROM senders WHERE username = :username", username = input_username)
            if len(rowssenders) != 1 or not check_password_hash(rowssenders[0]["password_hash"], input_password):
                rowsdispatcher = db.execute("SELECT * FROM dispatcher WHERE username = :username", username = input_username)
                # if not, check if the person signing in is a dispatcher
                if len(rowsdispatcher) != 1 or not check_password_hash(rowsdispatcher[0]["password_hash"], input_password):
                    flash("Username or password was incorrect")
                    return redirect("/signin")
                else:
                    # check if dispatcher is verified
                    rowsdispatcherapproval = db.execute("SELECT acceptance FROM dispatcher WHERE username = :username", username = input_username)
                    if rowsdispatcherapproval[0]["acceptance"] != "true":
                        return render_template("dispatcher-not-verified.html")
                    else:
                        session["user_id"] = rowsdispatcher[0]["id"]
                        session["role"] = "dispatcher"
                        return redirect("/dispatcher-dashboard")
            else:
                session["user_id"] = rowssenders[0]["id"]
                session["role"] = "sender"
                if rowssenders[0]["email_verified"] == "false":
                    flash("Your email is not verified. Verify your email to start using sendthis4me")
                return redirect("/sender-dashboard")
# SIGNUP =====================================================================================================
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/client-register", methods=["GET", "POST"])
def client_register():
    if request.method == 'GET':
        return render_template('client-register.html')
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        city = request.form.get("city")

        if not username or not password or not email:
            flash("Please fill in all required fields")
            return redirect("/signup")
        
        num = random.randrange(1, 10**7)
        new_id = '{:07}'.format(num)

        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        db.execute('INSERT INTO senders (id, username, password_hash, email, city, email_verified) VALUES (:id, :username, :password, :email, :city, :ver)',
            id = new_id,
            username = username, 
            password = password_hash, 
            email = email, 
            city = city,
            ver = "false"
        )
        new_user = db.execute("SELECT * FROM senders WHERE email = :email", email=email)
        msg = Message('Just one last step to register with Sendthis4me', sender = 'sendthis4me.noreply@gmail.com', recipients = [email])
        msg.html = render_template("!verification-email.html", newuser = new_user)
        mail.send(msg)

        return render_template("client-registration-confirmation.html")

@app.route("/sender-register", methods=["GET", "POST"])
def sender_register():
    if request.method == 'GET':
        return render_template('sender-register.html')
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        phone = request.form.get("phone")
        city = request.form.get("address")
        ordersPerWeek = request.form.get("week_availibility")
        vehicle = request.form.get("vehicle")
        id_number = request.form.get("id_number")
        licence_number = request.form.get("licence_number")
        num = random.randrange(1, 10**7)
        new_id = '{:07}'.format(num)

        if not username or not password or not email or not phone or not city or not id_number or not licence_number:
            flash("Please fill in all required fields")
            return redirect("/signup")

        # file.save(os.path.join(Config.UPLOAD_FOLDER, filename)
        passport_photo = request.files['photo_passport']
        passport_photo.save(os.path.join(UPLOAD_FOLDER, secure_filename(new_id + '_passport_photo.jpg')))

        licence_photo = request.files['licence_photo']
        licence_photo.save(os.path.join(UPLOAD_FOLDER, secure_filename(new_id + '_licence_photo.jpg')))

        photo = request.files['photo']
        photo.save(os.path.join(UPLOAD_FOLDER, secure_filename(new_id + '_photo.jpg')))

        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        db.execute('INSERT INTO dispatcher (id, username, password_hash, email, phone, dispatcher_address, orders_per_week, vehicle, passport_number, passport_photo_path, licence_number, licence_photo_path, photo, email_verified, acceptance) VALUES (:id, :username, :password, :email, :phone, :city, :opw, :v, :pn, :ppp, :ln, :lpp, :p, :email_verified, :acceptance)', 
            id = new_id,
            username = username, 
            password = password_hash, 
            email = email, 
            phone = phone, 
            city = city,
            opw = ordersPerWeek,
            v = vehicle,
            pn = id_number,
            ppp = "../static/uploads/"+secure_filename(new_id + '_passport_photo.jpg'),
            ln = licence_number,
            lpp = "../static/uploads/"+secure_filename(new_id + '_licence_photo.jpg'),
            p = "../static/uploads/"+secure_filename(new_id + '_photo.jpg'),
            email_verified = "false", 
            acceptance = "false"
        )
        new_user = db.execute("SELECT * FROM dispatcher WHERE email = :email", email=email)
        msg = Message('Verify your email address to register as dispatcher', sender = 'sendthis4me.noreply@gmail.com', recipients = [email])
        msg.html = render_template("!verification-email-dispatcher.html", newuser = new_user)
        mail.send(msg)
        return redirect("/sender-registration-confirmation")

@app.route("/verify-sender-email/<userid>")
def verify_email(userid):
    db.execute("UPDATE senders SET email_verified = 'true' WHERE id = :id", id=userid)
    new_user = db.execute("SELECT * FROM senders WHERE id = :id", id=userid)
    msg = Message('Getting started - Everything you need to know to get your parcels sent', sender = 'sendthis4me.noreply@gmail.com', recipients = [new_user[0]["email"]])
    msg.html = render_template("!welcome-email.html", newuser = new_user)
    mail.send(msg)
    return render_template("email-verification.html")

@app.route("/verify-dispatcher-email/<userid>")
def verify_email_dispatcher(userid):
    db.execute("UPDATE dispatcher SET email_verified = 'true' WHERE id = :id", id=userid)
    new_user = db.execute("SELECT * FROM dispatcher WHERE id = :id", id=userid)
    msg = Message('Email address verified successfully', sender = 'sendthis4me.noreply@gmail.com', recipients = [new_user[0]["email"]])
    msg.html = render_template("!welcome-email copy.html", newuser = new_user)
    mail.send(msg)
    return render_template("email-verification.html")


@app.route("/sender-registration-confirmation")
def sr_confirm():
    return render_template("sender-registration-confirmation.html")

@app.route("/client-registration-confirmation")
def cr_confirm():
    return render_template("client-registration-confirmation.html")

# NEW ORDER =====================================================================================================
@app.route("/new-order", methods=["GET", "POST"])
def new_order():
    if request.method == 'GET':
        current_user = db.execute("SELECT * FROM senders WHERE id = :id", id = session["user_id"])
        return render_template("new-order.html", username = current_user[0]["username"], user=current_user)
    else:
        current_user = db.execute("SELECT * FROM senders WHERE id = :id", id = session["user_id"])

        sender_name = request.form.get("sender-name")
        sender_phone = request.form.get("sender-phone")
        sender_address = request.form.get("sender-address")
        receiver_name = request.form.get("receiver-name")
        receiver_phone = request.form.get("receiver-phone")
        receiver_address = request.form.get("receiver-address")
        package_type = request.form.get("type")
        package_content = request.form.get("content")
        additional_notes = request.form.get("notes")
        payment_method = request.form.get("payment_method")

        if not sender_name or not sender_phone or not sender_address or not receiver_name or not receiver_phone or not receiver_address or not package_type or not package_content:
            flash("Please fill in all required fields")
            return redirect("/new-order")

        num = random.randrange(1, 10**7)
        new_id = '{:07}'.format(num)

        db.execute('INSERT INTO orders (id, sender_id, dispatcher_id, sender_name, sender_phone, sender_address, receiver_name, receiver_phone, receiver_address, content, package_category, notes, order_status, created, payment_method) VALUES (:id, :sender_id, :dispatcher_id, :sender_name, :sender_phone, :sender_address, :receiver_name, :receiver_phone, :receiver_address, :content, :package_category, :notes, :status, :created, :payment_method )', 
        id=new_id,
        sender_id = session["user_id"],
        dispatcher_id = 0,
        sender_name = sender_name,
        sender_phone = sender_phone,
        sender_address = sender_address,
        receiver_name = receiver_name,
        receiver_phone = receiver_phone,
        receiver_address = receiver_address,
        content = package_content,
        package_category = package_type,
        notes = additional_notes,
        status = 0,
        created = str(datetime.now()),
        payment_method = payment_method
        )
        current_order = db.execute("SELECT * FROM orders WHERE id = :id", id = new_id)

        msg = Message('You have placed a new order', sender = 'sendthis4me.noreply@gmail.com', recipients = [current_user[0]["email"]])
        msg.html = render_template("!neworder-email.html", newuser = current_user, neworder=current_order)
        mail.send(msg)
        flash("New order placed successfully")
        return redirect("/sender-dashboard")

@app.route("/new-order-confirmation")
def noc():
    current_username = db.execute("SELECT username FROM senders WHERE id = :id", id = session["user_id"])
    return render_template("new-order-confirmation.html", username = current_username[0]["username"])

@app.route("/dispatcher-dashboard")
def d_d():
    current_username = db.execute("SELECT username FROM dispatcher WHERE id = :id", id=session["user_id"])
    available_orders = db.execute("SELECT * FROM orders WHERE order_status = 1")
    pending_orders = db.execute("SELECT * FROM orders WHERE (order_status BETWEEN 1 AND 6) AND (dispatcher_id = :id) ", id=session["user_id"])
    completed_orders = db.execute("SELECT * FROM orders WHERE dispatcher_id = :id AND order_status = 7", id=session["user_id"])

    return render_template("sender-dashboard.html", username = current_username[0]['username'], available = available_orders, pending = pending_orders, completed = completed_orders)

@app.route("/sender-dashboard")
def s_d():
    current_username = db.execute("SELECT username FROM senders WHERE id = :id", id=session["user_id"])
    user_orders = db.execute("SELECT * FROM orders WHERE sender_id = :id", id=session["user_id"])
    unconfirmed_orders = db.execute("SELECT * FROM orders WHERE order_status = 0 AND sender_id = :id", id=session["user_id"])
    inprogress_orders = db.execute("SELECT * FROM orders WHERE order_status > 0 AND order_status < 7 AND sender_id = :id", id=session["user_id"])
    completed_orders = db.execute("SELECT * FROM orders WHERE order_status = 7 AND sender_id = :id", id=session["user_id"])

    return render_template("client-dashboard.html", username = current_username[0]["username"], unconfirmed = unconfirmed_orders, inprogress = inprogress_orders, completed = completed_orders, user = user_orders)

@app.route("/admin-dashboard")
def admin_dashboard():
        user = db.execute("SELECT * FROM admins WHERE id = :id", id = session["user_id"])
        dispatchers_unverified = db.execute("SELECT * FROM dispatcher WHERE acceptance = 'false'")
        dispatchers_verified = db.execute("SELECT * FROM dispatcher WHERE acceptance = 'true'")
        username = user[0]["username"]

        return render_template("admin-dashboard.html", unverified = dispatchers_unverified, verified = dispatchers_verified, username = username)

@app.route("/dispatcher/<did>", methods=["GET"])
def render_dispatcher(did):
    dispatcher = db.execute("SELECT * FROM dispatcher WHERE id = :id",id = did)
    return render_template("dispatcherbase.html", dispatcher = dispatcher)

@app.route("/order/<orderid>", methods=["GET"])
def render_order(orderid):
    order = db.execute("SELECT * FROM orders WHERE id = :id", id = orderid)
    if session["role"] == "sender":
        current_user = db.execute("SELECT * FROM senders WHERE id = :id", id = session["user_id"])
    elif session["role"] == "dispatcher":
        current_user = db.execute("SELECT * FROM dispatcher WHERE id = :id", id = session["user_id"])
    role = session["role"]
    username = current_user[0]["username"]

    if order[0]["order_status"] > 2:
        dispatcher = db.execute("SELECT * FROM dispatcher WHERE id = :id", id = order[0]["dispatcher_id"])
        dispatcher_name = dispatcher[0]["username"]
        return render_template("orderbase.html", order = order, username = username, role = role, name = dispatcher_name)
    else:
        return render_template("orderbase.html", order = order, username = username, role = role)
    

@app.route("/confirm-order/<orderid>")
def confirm_order(orderid):
    db.execute("UPDATE orders SET order_status = 1 WHERE id = :id", id = orderid)
    flash("Confirmed order successfully")
    return redirect("/sender-dashboard")


@app.route("/delete-order/<orderid>")
def delete_order(orderid):
    db.execute("DELETE * FROM orders WHERE = id = :id", id=orderid)
    return redirect("/sender-dashboard")

@app.route("/update-order/<orderid>")
def update_order_status(orderid):
    current = db.execute("SELECT order_status FROM orders WHERE id = :id", id=orderid)
    after = current[0]["order_status"] + 1
    db.execute("UPDATE orders SET order_status = :after WHERE id = :id", after=after, id=orderid)
    if after == 3:
        db.execute("UPDATE orders SET time3 = :time WHERE id = :id", time=str(datetime.now()), id=orderid)
    elif after == 4:
        db.execute("UPDATE orders SET time4 = :time WHERE id = :id", time=str(datetime.now()), id=orderid)
    elif after == 5:
        db.execute("UPDATE orders SET time5 = :time WHERE id = :id", time=str(datetime.now()), id=orderid)
    elif after == 6:
        db.execute("UPDATE orders SET time6 = :time WHERE id = :id", time=str(datetime.now()), id=orderid)
    elif after == 7:
        db.execute("UPDATE orders SET time7 = :time WHERE id = :id", time=str(datetime.now()), id=orderid)
    elif after == 8:
        db.execute("UPDATE orders SET time8 = :time WHERE id = :id", time=str(datetime.now()), id=orderid)
    
    
    order = db.execute("SELECT * FROM orders WHERE id = :orderid", orderid=orderid)

    dispatcher = db.execute("SELECT * FROM dispatcher WHERE id = :dispatcherid", dispatcherid=order[0]["dispatcher_id"])
    sender = db.execute("SELECT * FROM senders WHERE id = :senderid", senderid=order[0]["sender_id"])

    dispatcher_name = dispatcher[0]["username"]
    sender_name = sender[0]["username"]

    msg = Message('Order status updated', sender = 'sendthis4me.noreply@gmail.com', recipients = [sender[0]["email"]])
    msg.html = render_template("!orderupdated-email.html", sender = sender_name, dispatcher = dispatcher_name, order=order)
    mail.send(msg)
    flash("order status updated successfully")
    return redirect("/dispatcher-dashboard")

@app.route("/accept-order/<orderid>")
def accept_order(orderid):
    db.execute("UPDATE orders SET order_status = 2, dispatcher_id = :disid WHERE id = :id", id=orderid, disid = session["user_id"])
    db.execute("UPDATE orders SET time2 = :time WHERE id = :id", time=str(datetime.now()), id=orderid)

    order = db.execute("SELECT * FROM orders WHERE id = :orderid", orderid=orderid)

    dispatcher = db.execute("SELECT * FROM dispatcher WHERE id = :dispatcherid", dispatcherid=order[0]["dispatcher_id"])
    sender = db.execute("SELECT * FROM senders WHERE id = :senderid", senderid=order[0]["sender_id"])

    dispatcher_name = dispatcher[0]["username"]
    sender_name = sender[0]["username"]

    msg = Message('Your order has been accepted by a dispatcher', sender = 'sendthis4me.noreply@gmail.com', recipients = [sender[0]["email"]])
    msg.html = render_template("!orderaccepted-email.html", sender = sender_name, dispatcher = dispatcher_name, order=order)
    mail.send(msg)
    flash("Order accepted")
    return redirect("/dispatcher-dashboard")

@app.route("/verify-dispatcher/<did>")
def verify_dispatcher(did):
    db.execute("UPDATE dispatcher SET acceptance = 'true' WHERE id = :id", id=did)
    dispatcher = db.execute("SELECT * FROM dispatcher WHERE id = :id", id=did)
    flash("Dispatcher verified successfully")
    return redirect("/admin-dashboard")

@app.route("/suspend-dispatcher/<did>")
def suspend_dispatcher(did):
    db.execute("UPDATE dispatcher SET acceptance = 'false' WHERE id = :id", id=did)
    dispatcher = db.execute("SELECT * FROM dispatcher WHERE id = :id", id=did)
    return render_template("dispatcher-status-change.html", dispatcher=dispatcher)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/sender-settings")
def sender_settings():
    user = db.execute("SELECT * FROM senders WHERE id = :id", id = session["user_id"])
    username = user[0]["username"]
    return render_template("sender-settings.html", username = username)

@app.route("/change-password-sender", methods=["POST"])
def cps():
    user = db.execute("SELECT * FROM senders WHERE id = :id", id=session['user_id'])
    oldpass = request.form.get('old-pass')
    newpass = request.form.get('new-pass')
    if check_password_hash(user[0]["password_hash"], oldpass):
        db.execute("UPDATE senders SET password_hash = :password WHERE id = :id", id=session["user_id"], password=generate_password_hash(newpass))
    flash("Password changed successfully")
    return redirect("/sender-dashboard")

@app.route("/autofill-setup-sender", methods=["POST"])
def afs():
        autofill_name = request.form.get("sender-name")
        autofill_phone = request.form.get("sender-phone")
        autofill_address = request.form.get("sender-address")
        
        db.execute("UPDATE senders SET autofill_name = :name, autofill_phone = :phone, autofill_address = :address WHERE id = :id",
        phone = autofill_phone,
        name = autofill_name,
        address = autofill_address,
        id = session["user_id"]
        )
        flash("Autofill settings changes successfully")
        return redirect("/sender-dashboard")

@app.route("/dispatcher-settings")
def dispatcher_settings():
    user = db.execute("SELECT * FROM dispatcher WHERE id = :id", id = session["user_id"])
    username = user[0]["username"]
    return render_template("dispatcher-settings.html", username = username)

@app.route("/change-password-dispatcher", methods=["POST"])
def pd():
    user = db.execute("SELECT * FROM dispatcher WHERE id = :id", id=session['user_id'])
    oldpass = request.form.get('old-pass')
    newpass = request.form.get('new-pass')
    if check_password_hash(user[0]["password_hash"], oldpass):
        db.execute("UPDATE dispatcher SET password_hash = :password WHERE id = :id", id=session["user_id"], password=generate_password_hash(newpass))
    flash("Password changed successfully")
    return redirect("/dispatcher-dashboard")

@app.route("/register-admin", methods=["GET", "POST"])
def register_admin():
    if request.method == "GET":
        return render_template("/admin-register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        db.execute("INSERT INTO admins (username, password_hash) VALUES (:username, :password)", 
        username=username, 
        password=generate_password_hash(password) 
        )
        flash("Admin signed up successfully")
        return redirect("/admin-dashboard")
