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

# Load variables from .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    
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

    


    #Display home page
    @app.route("/homePage")
    def homePage():
        is_admin = session.get('is_admin', False)

        #Connect to database
        conn = get_db_connection()
        cur = conn.cursor()
        
        #Grabs list of events to display in event menu on home page
        cur.execute('SELECT * FROM events;')
        events = cur.fetchall()
        #Print statement for TESTING
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
                event[7]   # Background image filename
            )
            formatted_dates.append(updated_event)
        #Print statement for TESTING
        print(formatted_dates)

        #Testing with admin view CHANGE TO FALSE LATER
        adminStatus = True
        #if session['email'] == 'omkar@gmail.com':
        #    adminStatus = True
        
        #Passes in list of events (with formatted dates) and admin status to home page
        return render_template("index.html", events = formatted_dates, admin = is_admin)
    


    
    @app.route("/add_event", methods=['POST'])
    def add_event():
        print("entered 1")
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location']
        contact_email = request.form['contact_email']
        background_image = request.form['background_image']  # Just the file name, not upload

        try:
            print("entered 2")

            #Connect to database
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO events (name, date, start_time, end_time, location, contact, file_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (event_name, event_date, start_time, end_time, location, contact_email, background_image))

            #Commit changes to database and close database connection
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print("entered 3")
            print("Database error:", e)

        return redirect(url_for('homePage'))



    #Display calendar page
    @app.route("/calendar")
    def calendar():
        return render_template("calendar.html")
    
    #Display event signup (based on id in SQL events table)
    @app.route("/signup/<int:event_id>")
    def viewEvent(event_id):
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
            event_data[0][7]   # Background image filename
        )
        #Print statement for TESTING
        print(updated_event)

        '''
        filename = event_data[0][0].replace(' ', '-').lower() + '-' + str(event_data[0][1]) + '.html'
        print(filename)
        '''

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




    @app.route("/add_table/<int:event_id>", methods=['POST'])
    def add_table(event_id):
        print("entered add table")
        category = request.form['category']
        max_entries = request.form['max_entries']
        vieworder = request.form['vieworder']

        try:
            print("entered try")
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO event_tables (event_id, table_name, maxentries,vieworder)
                VALUES (%s, %s, %s, %s)
            """, (event_id, category, max_entries,vieworder,))

            #Commit changes to database and close database connection
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)

        return redirect(url_for('viewEvent', event_id = event_id))




    @app.route('/signup/<int:table_id>', methods=['POST'])
    def signup(table_id):
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

        cur.execute('SELECT first_name, last_name FROM public.user WHERE email = %s', (email,))
        #Data is in within a tuple inside a list: [(first_name, last_name)]
        #Concacatenates with a space in between to get full name
        nameData = cur.fetchall()
        person = nameData[0][0] + ' ' + nameData[0][1]

        cur.execute('INSERT INTO event_signups (table_id, responsible_name, item_name, responsible_email, comment) VALUES (%s, %s, %s, %s, %s)', (table_id, person, dish, email, comment))
 
        #Commit changes to database and close database connection
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('viewEvent', event_id = eventID))




    #Admin Code update for login
    @app.route("/", methods=['GET','POST'])
    def index():
        form = LoginForm()
        print("before validate event")
        if form.validate_on_submit:
            print("inside validate_on_submit")
            try:
                user = User.query.filter_by(email=form.email.data).first()
                print("successfully logged in")
                if user and bcrypt.check_password_hash(user.password, form.password.data):
                    is_admin=user.is_admin
                    #if 'adminCode' in session and session['adminCode'] == app.config['ADMIN_CODE']:
                    if form.adminCode.data and form.adminCode.data == int(os.getenv('ADMIN_CODE')):
                        print("You are an admin!")
                        user.is_admin=True
                        db.session.commit()
                        is_admin=True
                    else:
                        is_admin=user.is_admin
                    session['email'] = user.email
                    session['is_admin'] = is_admin
                    db.session.commit()
                    print("successfully validated user")
                    return redirect(url_for('homePage'))
                    #return render_template("homePage.html", is_admin=is_admin)
                else:
                    print("Error validating user. Please check email and password")
            except Exception as e:
                print(e)
            
        else:
            return render_template("login.html", form = form)
        return render_template("login.html", form = form)
    



    @app.route("/register", methods=['GET','POST'])
    def register():
        print("entered register")
        form = RegisterForm()
        if form.email.data is not None and form.password.data is not None:
            print("entered first if")
            if form.validate_on_submit:
                print("entered second if")
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
                    print("entered try")
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('index'))
                    #return render_template("login.html", form = form)
                except Exception as e:
                    db.session.rollback()
                    print(e)

        return render_template("register.html", form = form)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
