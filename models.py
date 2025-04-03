from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    #id = db.Column(db.Integer, primary_key = True)
    #username = db.Column(db.String(200), unique=True, nullable=False, primary_key = True)
    email = db.Column(db.String(200), unique=True, nullable=False, primary_key = True)
    firstName = db.Column(db.String(200), nullable=False)
    lastName = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    grade = db.Column(db.String(2), nullable=True)

#Create event model
#Admin creates new event
    
# #add column for when event was created
# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(400), unique = True, nullable=False)
#     date = db.Column(db.DateTime, nullable = False)
#     location = db.Column(db.String(200), nullable = False)
#     eventCoordinater = db.Column(db.String(200), db.ForeignKey('user.email'))

# #Event coordinater creates items for students to signup for    
# class AddEventItem(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     eventId = db.Column(db.Integer, db.ForeignKey('events.id'))
#     item = db.Column(db.String(400), nullable = False)
#     availableSlots = db.Column(db.Integer, nullable = False)

# #User item signup
# class EventSignup(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     eventId = db.Column(db.Integer, db.ForeignKey('events.id'))
#     itemId = db.Column(db.String(200), db.ForeignKey('AddEventItem.id'))
#     studentEmail = db.Column(db.String(200), db.ForeignKey('user.email'))
#     availableSlots = db.Column(db.Integer, nullable = False)
#     dishName = db.Column(db.String(400), nullable = False)
#     dairy = db.Column(db.Boolean, default = True)
#     gluten = db.Column(db.Boolean, default = True)
#     meat = db.Column(db.Boolean, default = True)
#     eggs = db.Column(db.Boolean, default = True)
#     fish = db.Column(db.Boolean, default = True)
#     nuts = db.Column(db.Boolean, default = True)
#     comments = db.Column(db.String(400), nullable = True)


    
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class User(db.Model):
#     # id = db.Column(db.Integer, primary_key = True)
#     email = db.Column(db.String(200), primary_key = True, unique=True, nullable=False)
#     password = db.Column(db.String(500), nullable=False)
#     code = db.Column(db.Integer, nullable=True)
    





# using System.Collections;
# using System.Collections.Generic;
# using UnityEngine;

# public class Projectile : MonoBehaviour
# {
#     [field: SerializeField]
#     public float Speed { get; private set; } = 2;
#     [field: SerializeField]
#     public float Damage { get; private set; } = 1;
#     [field: SerializeField]
#     public Transform Target { get; set; }

#     void Start()
#     {

#     }
#     void Update()
#     {
#         if (Target != null)
#         {
#             transform.position = Vector3.MoveTowards(transform.position, Target.transform.position, Time.deltaTime * Speed);
#             transform.LookAt(Target.transform);
#             Target.transform.position, Time.deltaTime * Speed)
#         float distance = Vector3.Distance(transform.position, Target.transform.position);
#         if (distance <= 0.2)
#         {
#             Health health = Target.GetComponentInParent<health>();
            
#         }
#     }
# }
