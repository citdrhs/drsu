from flask import Flask, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm
from models import db, User
from flask_bcrypt import Bcrypt
import os
import psycopg2
from dotenv import load_dotenv
from collections import defaultdict


# Load variables from .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
    
    bcrypt = Bcrypt()

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
    
    #Display home page
    @app.route("/homePage")
    def homePage():
         return render_template("index.html")
    
    #Display calendar page
    @app.route("/calendar")
    def calendar():
        return render_template("calendar.html")
    
    #Display event signup (based on id in SQL events table)
    @app.route("/signup/<int:signup_id>")
    def signup(signup_id):
        conn = get_db_connection()
        cur = conn.cursor()
        #Adding in data to test table to test
        cur.execute('DROP TABLE IF EXISTS test_signup_id;')
        cur.execute('CREATE TABLE test_signup_id (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, event_name TEXT);')
        cur.execute('INSERT INTO test_signup_id (event_name)'
                    'VALUES (%s)',
                    ('Thanksgiving Feast',)
        )
        conn.commit()


        cur.execute('SELECT * FROM test_signup_id WHERE id = %s', (signup_id,))
        #Converts event name into HTML filename by:
        #Replacing all spaces with dashes, making it all lowercase, and adding '-[id#].html' to the end
        #Ex. If Freshman-Sophomore Social has an id of 3:
        #Freshman-Sophomore Social --> freshman-sophomore-social-3.html
        event_data = cur.fetchall()
        filename = event_data[0][1].replace(' ', '-').lower() + '-' + str(event_data[0][0]) + '.html'
        
        #Add GROUP BY item to group it by appetizer, dessert, etc. (might need to SELECT item and GROUP, then join to the rest of table to avoid error)
        cur.execute('SELECT * FROM test_event_signup WHERE event_id = %s', (signup_id,))
        signup_data = cur.fetchall()
        print(signup_data)

        #Sort table by item column (appetizer, dessert, etc.)        
        signup_data_sorted = sorted(signup_data, key=lambda signup: signup[2])
        for signup in signup_data_sorted:
            print(signup)

        
        signup_dict = {}
        
        #Start index where the dictionary starts selecting data from
        startIndex = 0

        #Item name is appetizer, dessert, etc.
        for index in range(len(signup_data_sorted)):
            previousItemName = signup_data_sorted[index-1][2]
            currentItemName = signup_data_sorted[index][2]
            if index > 0 and (currentItemName != previousItemName):
                #Once a new item name is recognized, assigns the rows up to the new item name to the item name
                #Ex. All the appetizer data rows are assigned to the key 'Appetizer';
                signup_dict[previousItemName] = signup_data_sorted[startIndex:index]
                startIndex = index
            if index == len(signup_data_sorted)-1:
                signup_dict[currentItemName] = signup_data_sorted[startIndex:]

        print(signup_dict)

        cur.close()
        conn.close()
        return render_template(filename, event_name = 'Thanksgiving Feast', location = 'Commons 1', signup_tables = signup_dict)
    
    @app.route('/delete_signup/<int:id>/')
    def delete_signup(id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT event_id FROM test_event_signup WHERE id = %s', (id,))
        eventID = cur.fetchall()
        cur.execute('DELETE FROM test_event_signup WHERE id = %s', (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('signup', signup_id = eventID[0][0]))

    @app.route("/", methods=['GET','POST'])
    def index():
        form = LoginForm()
        print("before validate event")
        if form.validate_on_submit():
            print("inside validate_on_submit")
            try:
             user = User.query.filter_by(email=form.email.data).first()
             print("successfully logged in")
            except Exception as e:
                print(e)
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session['email'] = user.email
                print("successfully validated user")
                return redirect(url_for('homePage'))
            else:
                print("Error validating user. Please check email and password")
        else:
            return render_template("login.html", form = form)
    
    @app.route("/register", methods=['GET','POST'])
    def register():
        form = RegisterForm()
        if form.email.data is not None and form.password.data is not None:
            if form.validate_on_submit:
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(
                    email=form.email.data,
                    password=hashed_password,
                    firstName=form.firstName.data,
                    lastName=form.lastName.data,
                    grade=form.grade.data
                )
                try:
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('index'))
                except Exception as e:
                    db.session.rollback()
                    print(e)

        return render_template("register.html", form = form)
    
    #Test to see users displayed - DELETE LATER FOR SECURITY PURPOSES!
    @app.route("/displayNames")
    def displayNames():
        users = User.query.all()
        return {user.email: user.password for user in users}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


# from flask import Flask, request, render_template, redirect, session
# from flask_sqlalchemy import SQLAlchemy
# from forms import LoginForm, RegisterForm
# import bcrypt

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://potluck_signup:C1TP0tluck!@drhscit.org:5432/potluckdb'
# db = SQLAlchemy(app)
# app.secret_key = 'secret_key'

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))

#     def __init__(self,email,password):
#         self.email = email
#         self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
#     def check_password(self,password):
#         return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

# with app.app_context():
#     db.create_all()


# @app.route('/')
# def index():
#     return render_template('home.html')

# @app.route('/register',methods=['GET','POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         # handle request
#         email = request.form['email']
#         password = request.form['password']

#         new_user = User(email=email,password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         db.session.rollback()
        
#         print("Committed")
#         return redirect('/login')

#     return render_template('register.html')

# @app.route('/login',methods=['GET','POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         email = request.form['email']
#         password = request.form['password']

#         user = User.query.filter_by(email=email).first()
        
#         if user and user.check_password(password):
#             session['email'] = user.email
#             return redirect('/dashboard')
#         else:
#             return render_template('login.html',error='Invalid user')

#     return render_template('login.html')

# if __name__ == '__main__':
#     app.run(debug=True)





















# # from flask import Flask, render_template, url_for, redirect
# # from forms import LoginForm, RegisterForm
# # from models import db, User 
# # from flask_bcrypt import Bcrypt
# # from flask_sqlalchemy import SQLAlchemy


# # def create_app():
# #     app = Flask(__name__)
# #     app.config['SECRET_KEY'] = 'mysecretkey'
# #     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://potluck_signup:C1TP0tluck!@drhscit.org:5432/potluckdb'
    
# #     db = Postdb.connect(host="localhost", user="root", passwd="", db="osn")
# #     cur = db.cursor()

# #     bcrypt = Bcrypt()

# #     db.init_app(app)
# #     bcrypt.init_app(app)

# #     with app.app_context():
# #         db.create_all()


# #     @app.route("/")
# #     def index():
# #         return render_template("home.html")
    
# #     @app.route("/login")
# #     def login():
# #         loginform = LoginForm()
# #         return render_template("login.html", form = loginform)
    
# #     @app.route("/register", methods = ['GET', 'POST', 'PUT'])
# #     def register():
# #         form = RegisterForm()
# #         if form.validate_on_submit():
# #             hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
# #             user = User(email=form.email.data, password = hashed_password, code=form.code.data)
# #             cur.execute(
# #             """INSERT INTO 
# #             user (
# #             fname,
# #             lname,
# #             username,
# #             password,
# #             email,
# #             question,
# #             answer)
# #             VALUES (%s,%s)""", (user.email, user.password))
# #             db.commit()
# #             print ("Registered")
# #             db.session.commit(user)
# #             return redirect(url_for('login'))
# #         return render_template("register.html", form = RegisterForm)
    
# #     return app

# # if __name__ == '__main__':
# #     app = create_app()
# #     app.run(debug=True, port=5001)
