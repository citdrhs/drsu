from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    #id = db.Column(db.Integer, primary_key = True)
   # username = db.Column(db.String(200), unique=True, nullable=False, primary_key = True)
    email = db.Column(db.String(200), unique=True, nullable=False, primary_key = True)
    password = db.Column(db.String(500), nullable=False)
    
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class User(db.Model):
#     # id = db.Column(db.Integer, primary_key = True)
#     email = db.Column(db.String(200), primary_key = True, unique=True, nullable=False)
#     password = db.Column(db.String(500), nullable=False)
#     code = db.Column(db.Integer, nullable=True)
    
