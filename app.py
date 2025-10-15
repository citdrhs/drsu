from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm
from models import db, User
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import flash
from better_profanity import profanity
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message


#==================================================================================================================================================================#
#                                                                                                                                                                  #
#Project: CIT Signups                                                                                                                                              #
#Contact: Lynne Norris (lmnorris@henrico.k12.va.us)                                                                                                                #
#                                                                                                                                                                  #
#Deep Run High School Restricted                                                                                                                                   #
#                                                                                                                                                                  #
#DO NOT MODIFY                                                                                                                                                     #
#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#@brief Has Flask frontend/backend integration                                                                                                                     #
#                                                                                                                                                                  #
#@author Omkar Deshmukh | (hcps-deshmukop@henricostudents.org), Jack Gardner | (hcps-gardnejk1@henricostudents.org), Zachary Lin | (hcps-linzc@henricostudents.org)#                                                 
#                                                                                                                                                                  #
#@version 1.0                                                                                                                                                      #
#                                                                                                                                                                  #
#@date Date_Of_Creation 2/2/25                                                                                                                                     #
#                                                                                                                                                                  #
#@date Last_Modification 4/17/25                                                                                                                                   #
#                                                                                                                                                                  #
#==================================================================================================================================================================#


# Load variables from .env
load_dotenv()
profanity.load_censor_words()
app = Flask(__name__)
#global_app = None
def create_app():
    #app = Flask(__name__)
    
   # global global_app
    #app=Flask(__name__)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Or another SMTP server
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
    mail = Mail(app)

    def generate_confirmation_token(email):
        print("entered generate token")
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(email, salt='email-confirm-salt')

    def confirm_token(token, expiration=3600):
        print("entered confirm token")
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token, salt='email-confirm-salt', max_age=expiration)
        except:
            return False
        return email
    def send_confirmation_email(user_email):
        print("entered send email")
        token = generate_confirmation_token(user_email)
        print("1")
        confirm_url = url_for('confirm_email', token=token, _external=True)
        print("2")
        html = render_template('confirm_email.html', confirm_url=confirm_url)
        print("3")
        msg = Message("Confirm Your Registration", sender=app.config['MAIL_USERNAME'], recipients=[user_email])
        print("4")
        msg.html = html
        print("sending")
        mail.send(msg)
    
    @app.route('/confirm/<token>/')
    #@app.route('/confirm/<token>')
    def confirm_email(token):
        print("entered confirm email")
        email = confirm_token(token)
        if not email:
            flash("The confirmation link is invalid or has expired.", "danger")
            return redirect(url_for('register'))

        pending_user = session.get('pending_user')
        if not pending_user or pending_user['email'] != email:
            flash("No matching pending registration found.", "danger")
            return redirect(url_for('register'))

        new_user = User(**pending_user)
        db.session.add(new_user)
        db.session.commit()
        session.pop('pending_user', None)

        flash("Registration confirmed! You can now log in.", "success")
        return redirect(url_for('index'))


    
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
    
    bcrypt = Bcrypt()
    #csrf = CSRFProtect(app)

    with app.app_context():
        db.init_app(app)
        bcrypt.init_app(app)
        db.create_all()

    #Establishes connection with database
    def get_db_connection():
        conn = psycopg2.connect(
            host='drhscit.org', 
            database=os.environ.get('DB'),
            user=os.environ.get('DB_UN'), 
            password=os.environ.get('DB_PW')
        )
        print('db connected')
        return conn
    
    #Formats date name to text, ex. 2012-04-13 --> April 13th, 2012
    def format_date_with_suffix(date_obj):
        day = date_obj.day
        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return date_obj.strftime(f"%A, %B {day}{suffix}, %Y")

    #testing
    @app.route("/burp")
    def burp():
        return "burp"

    #Admin Code update for login
    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/", methods=['GET', 'POST'])
    @app.route("/", methods=['GET', 'POST'])
    def index():
        form = LoginForm()
        print("before validate event")

        if request.method == 'POST':
            print("entered post")
            if form.validate_on_submit:
                print("inside validate_on_submit")
                try:
                    user = User.query.filter_by(email=form.email.data).first()
                    if user:
                        print("User exists")
                        if bcrypt.check_password_hash(user.password, form.password.data):
                            is_admin = user.is_admin

                            
                            if form.adminCode.data:
                                print("entered if")
                                try:
                                    print("Entered try")
                                    admin_code = int(form.adminCode.data)
                                    
                                    if admin_code == int(os.environ.get('ADMIN_CODE')):
                                        print("You are an admin!")
                                        user.is_admin = True
                                        db.session.commit()
                                        is_admin = True
                                except ValueError:
                                    flash("Invalid admin code format.", "danger")

                            
                            session['email'] = user.email
                            session['is_admin'] = is_admin
                            print("successfully validated user")
                            return redirect(url_for('homePage'))
                        else:
                            flash("Incorrect password. Please try again.", "danger")
                            print("Incorrect password")
                    else:
                        flash("Email does not exist. Please sign up or try again.", "danger")
                        print("Email does not exist")
                except Exception as e:
                    print(e)
                    flash("An error occurred while trying to log in. Please try again.", "danger")

        
        return render_template("login.html", form=form)
    
    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/logout/", methods=['GET', 'POST'])
    @app.route("/logout", methods=['GET', 'POST'])
    def logout():
        session.clear()
        return redirect(url_for('index'))
    
    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/register/", methods=['GET', 'POST'])
    @app.route("/drsu/register", methods=['GET', 'POST'])
    def register():
        form = RegisterForm()

        if request.method == 'POST':
            if form.validate_on_submit:
                existing_user = User.query.filter_by(email=form.email.data).first()
                if profanity.contains_profanity(form.first_name.data) or profanity.contains_profanity(form.last_name.data):
                    flash("No use of profanity allowed.", "danger")
                    return redirect(url_for('register'))
                if existing_user:
                    flash("Email is already in use. Please choose a different one.", "danger")
                    return redirect(url_for('register'))
                
                if form.password.data != form.confirmPassword.data:
                    flash("Passwords do not match!", "danger")
                    return redirect(url_for('register'))

                
                if len(form.password.data) < 8:
                    flash("Password must be at least 8 characters long.", "danger")
                    return redirect(url_for('register'))

                
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=hashed_password,
                    grade=form.grade.data,
                    is_admin=form.is_admin.data
                )

                try:
                    session['pending_user'] = {
                        "email": form.email.data,
                        "first_name": form.first_name.data,
                        "last_name": form.last_name.data,
                        "password": bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
                        "grade": form.grade.data,
                        "is_admin": form.is_admin.data
                    }
                    send_confirmation_email(form.email.data)
                    flash("A confirmation email has been sent. Please check your inbox.", "info")
                    return redirect(url_for('index'))
                except Exception as e:
                    db.session.rollback()
                    #flash(f"An error occurred: {e}", "danger")
                    print(e)
            
        return render_template("register.html", form=form)

    #Display home page
    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/homePage/")
    @app.route("/homePage")
    def homePage():
        if 'email' not in session:
            return redirect(url_for('index'))

        is_admin = session.get('is_admin', False)

        #Connect to database
        conn = get_db_connection()
        cur = conn.cursor()

        #Grabs list of events to display in event menu on home page
        cur.execute('SELECT t1.*,t2.first_name,t2.last_name FROM events AS t1 JOIN public.user AS t2 ON t2.email=t1.contact;')
        events = cur.fetchall()
        #Print statement for TESTING
        print("These are the events")
        print(events)

        #List of events with formatted dates
        formatted_dates = []
        
        #Formats date name for each event
        for event in events:
            #Formats date name to text, ex. 2012-04-13 --> April 13th, 2012
            formatted_date = format_date_with_suffix(event[2])
            updated_event = (
                event[0],  # ID
                event[1],  # Name
                formatted_date,  # Formatted Date
                event[3],  # Start Time
                event[4],  # End Time
                event[5],  # Location
                event[6],  # Email
                event[7],   # Background image filename
                event[8],
                event[9],
                event[10],
                event[2]
            )
            formatted_dates.append(updated_event)
        #Print statement for TESTING
        print(formatted_dates)

        #Testing with admin view CHANGE TO FALSE LATER
        adminStatus = True
        #if session['email'] == 'omkar@gmail.com':
        #    adminStatus = True
        
        #Passes in list of events (with formatted dates) and admin status to home page

        return render_template("index.html", events = formatted_dates, admin = is_admin, email = session.get('email'))
    
    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/add_event/", methods=['POST'])
    @app.route("/add_event", methods=['POST'])
    def add_event():
        event_id = request.form.get('event_id')
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location']
        contact_email = request.form['contact_email']
        event_note = request.form['note']

        background_file = request.files.get('background_image')
        filename = None

        if background_file and background_file.filename:
            filename = secure_filename(background_file.filename)
            basedir = os.path.dirname(__file__)
            image_folder = os.path.join(basedir, 'static', 'images')
            background_file.save(os.path.join(image_folder, filename))

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            if event_id:
                # Update event
                if filename: # if there is a background
                    cur.execute("""
                        UPDATE events
                        SET name=%s, date=%s, start_time=%s, end_time=%s, location=%s,
                            contact=%s, file_name=%s, event_note=%s
                        WHERE id=%s
                    """, (event_name, event_date, start_time, end_time, location,
                        contact_email, filename, event_note, event_id))
                else: # edit without background
                    cur.execute("""
                        UPDATE events
                        SET name=%s, date=%s, start_time=%s, end_time=%s, location=%s,
                            contact=%s, event_note=%s
                        WHERE id=%s
                    """, (event_name, event_date, start_time, end_time, location,
                        contact_email, event_note, event_id))
            else:
                # Add new event if event doesnt already exist
                cur.execute("""
                    INSERT INTO events (name, date, start_time, end_time, location, contact, file_name, event_note)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (event_name, event_date, start_time, end_time, location, contact_email, filename, event_note))

            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)

        return redirect(url_for('homePage'))

    #Display calendar page
    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/calendar/")
    @app.route("/calendar")
    def calendar():
        if 'email' not in session:
            return redirect(url_for('index'))

        return render_template("calendar.html")
    
    #Display event signup (based on id in SQL events table)
    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/viewEvent/<int:event_id>/")
    @app.route("/viewEvent/<int:event_id>")
    def viewEvent(event_id):
        if 'email' not in session:
            return redirect(url_for('index'))

        is_admin = session.get('is_admin', False)

        session_email = session.get('email')
        
        print('event_id again')
        print(event_id)

        #Connect to database
        conn = get_db_connection()
        cur = conn.cursor()
        '''
        cur.execute('SELECT t1.name,t1.id FROM test_events as t1 JOIN event_tables as t2 ON t1.id=t2.event_id WHERE t1.id = %s', (event_id,))
        #Converts event name into HTML filename by:
        #Replacing all spaces with dashes, making it all lowercase, and adding '-[id#].html' to the end
        #Ex. If Freshman-Sophomore Social has an id of 3:
        #Freshman-Sophomore Social --> freshman-sophomore-social-3.html
        '''
        cur.execute('SELECT * from events where id = %s', (event_id,))
        event_data = cur.fetchall()
        print(event_data)
        
        #Formats date name to text, ex. 2012-04-13 --> April 13th, 2012
        formatted_date = format_date_with_suffix(event_data[0][2])
        updated_event = (
            event_data[0][0],  # ID
            event_data[0][1],  # Name
            formatted_date,  # Formatted Date
            event_data[0][3],  # Start Time
            event_data[0][4],  # End Times
            event_data[0][5],  # Location
            event_data[0][6],  # Email
            event_data[0][7],   # Background image filename
            event_data[0][8]   # Note to users
        )
        #Print statement for TESTING
        print(updated_event)

        cur.execute('SELECT * FROM event_tables WHERE event_id = %s order by vieworder', (event_id,))
        tables = cur.fetchall()
        print(tables)
        
        signup_dict = {}
        max_entries_dict = {}

        for table in tables:
            table_id = table[0]
            category = table[2]
            max_entries = table[3]

            cur.execute('SELECT * FROM event_signups WHERE table_id = %s', (table_id,))
            data = cur.fetchall()
            print("table id:")
            print(table_id)
            print(data)

            signup_dict[category] = data
            max_entries_dict[category] = max_entries

        #Print statement for TESTING
        print(signup_dict)

        #Print statement for TESTING
        print("event data")
        print(event_data)
        
        #Grabs name of event contact by referencing their email
        cur.execute('SELECT first_name, last_name FROM public.user WHERE email = %s', (updated_event[6],))
        #Data is in within a tuple inside a list: [(first_name, last_name)]
        #Concacatenates with a space in between to get full name
        nameData = cur.fetchall()
        contact_name = nameData[0][0] + ' ' + nameData[0][1]

        session_email = session.get('email')
        if session_email == updated_event[6]:
            is_admin = True

        cur.execute('SELECT first_name, last_name FROM public.user WHERE email = %s', (session_email,))
        name_data = cur.fetchall()
        full_name = name_data[0][0] + " " + name_data[0][1]
        
        #Close database connection
        cur.close()
        conn.close()

        return render_template(
            'signup_base.html',
            signup_tables=signup_dict,
            max_entries = max_entries_dict,
            tables = tables,
            event_data = updated_event,
            contact_name = contact_name,
            admin = is_admin,
            name = full_name,
            email = session_email
        )

    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route('/signup/<int:table_id>/', methods=['POST'])
    @app.route('/signup/<int:table_id>', methods=['POST'])
    def signup(table_id):
        print("entered")
        #Email taken from the current user's email 
        email = session.get('email')
        
        #Dish and comments taken from user input
        dish = request.form['dish']
        comment = request.form.get('extras', '')

        #Connect to database
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT event_id FROM event_tables WHERE id = %s', (table_id,))
        #Data is in within a tuple inside a list: [(id)] so cur.fetchall()[0][0] is needed to grab the actual number
        eventID = cur.fetchall()[0][0]
        print("EventID right here")
        print(eventID)
        
        if profanity.contains_profanity(dish) or profanity.contains_profanity(comment):
            flash("Profanity is not allowed in the signup. Please remove inappropriate language.", "danger")
            return redirect(url_for('viewEvent', event_id=eventID))

        cur.execute('SELECT first_name, last_name FROM public.user WHERE email = %s', (email,))
        #Data is in within a tuple inside a list: [(first_name, last_name)]
        #Concacatenates with a space in between to get full name
        nameData = cur.fetchall()
        person = nameData[0][0] + ' ' + nameData[0][1]

        cur.execute('INSERT INTO event_signups (table_id, responsible_name, item_name, responsible_email, comment) VALUES (%s, %s, %s, %s, %s)', (table_id, person, dish, email, comment))
        print("Succesfully added")
        #Commit changes to database and close database connection
        conn.commit()
        cur.close()
        conn.close()
        flash("Signup confirmed!", "success")
        return redirect(url_for('viewEvent', event_id = eventID))

    #uses different function because signup id is needed not tbale id
    #@app.route('/edit_signup/<int:table_id>/', methods=['POST'])
    @app.route('/edit_signup/<int:id>', methods=['POST'])
    def edit_signup(id):
        print("entered edit signup")
        email = session.get('email')
        dish = request.form['dish']
        comment = request.form.get('extras', '')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT table_id FROM event_signups WHERE id = %s', (id,))
        table_id = cur.fetchone()[0]

        cur.execute('SELECT event_id FROM event_tables WHERE id = %s', (table_id,))
        event_id = cur.fetchone()[0]

        if profanity.contains_profanity(dish) or profanity.contains_profanity(comment):
            flash("Profanity is not allowed in the signup. Please remove inappropriate language.", "danger")
            return redirect(url_for('viewEvent', event_id=event_id))

        cur.execute('''
            UPDATE event_signups
            SET item_name = %s, comment = %s
            WHERE id = %s AND responsible_email = %s
        ''', (dish, comment, id, email))

        conn.commit()
        cur.close()
        conn.close()

        flash("Signup updated successfully!", "success")
        return redirect(url_for('viewEvent', event_id=event_id))

    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route('/delete_signup/<int:id>/')
    @app.route('/delete_signup/<int:id>/')
    def delete_signup(id):

        print("delete signup")

        #Connect to database
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT t1.event_id FROM event_tables as t1 Join event_signups as t2 On t1.id=t2.table_id WHERE t2.id = %s', (id,))
        #Data is in within a tuple inside a list: [(id)] so cur.fetchall()[0][0] is needed to grab the actual number
        eventID = cur.fetchall()[0][0]
        cur.execute('DELETE FROM event_signups WHERE id = %s', (id,))
        
        #Commit changes to database and close database connection
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('viewEvent', event_id = eventID))

    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route('/delete_table/<int:id>/')
    @app.route('/delete_table/<int:id>/')
    def delete_table(id):

        #Connect to database
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT event_id FROM event_tables WHERE id = %s', (id,))
        #Data is in within a tuple inside a list: [(id)] so cur.fetchall()[0][0] is needed to grab the actual number
        eventID = cur.fetchall()[0][0]
        cur.execute('DELETE FROM event_tables WHERE id = %s', (id,))
        
        #Commit changes to database and close database connection
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('viewEvent', event_id = eventID))

    #Route below is for testing on the server, Switch commenting when not testing on server
    #@app.route("/add_table/<int:event_id>/", methods=['POST'])
    @app.route("/add_table/<int:event_id>", methods=['POST'])
    def add_table(event_id):
        category = request.form['category']
        max_entries = request.form['max_entries']
        vieworder = request.form['vieworder']
        table_id = request.form.get('table_id')

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            if table_id:
                # Update existing table
                cur.execute("""
                    UPDATE event_tables
                    SET table_name = %s, maxentries = %s, vieworder = %s
                    WHERE id = %s
                """, (category, max_entries, vieworder, table_id))
            else:
                # Add new table
                cur.execute("""
                    INSERT INTO event_tables (event_id, table_name, maxentries, vieworder)
                    VALUES (%s, %s, %s, %s)
                """, (event_id, category, max_entries, vieworder))

            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)

        return redirect(url_for('viewEvent', event_id=event_id))

    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5032)
