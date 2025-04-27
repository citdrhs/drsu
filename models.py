from flask_sqlalchemy import SQLAlchemy

#==================================================================================================================================================================#
#                                                                                                                                                                  #
#Project: CIT Signups                                                                                                                                              #
#Contact: Lynne Norris (lmnorris@henrico.k12.va.us)                                                                                                                #
#                                                                                                                                                                  #
#Deep Run High School Restricted                                                                                                                                   #
#                                                                                                                                                                  #
#DO NOT MODIFY                                                                                                                                                     #
#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#@brief Has User table(flask) for Login and Register forms                                                                                                         #
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



db = SQLAlchemy()

class User(db.Model):
    email = db.Column(db.String(200), unique=True, nullable=False, primary_key = True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    is_admin = db.Column(db.Boolean, nullable = False)
    grade = db.Column(db.String(2), nullable=True)

