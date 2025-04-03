from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegisterForm(FlaskForm):
    #username = StringField('Username', validators= [DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    firstName = StringField('FirstName', validators = [DataRequired()])
    lastName = StringField('LastName', validators = [DataRequired()])
    grade = IntegerField('grade')
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Sign In')

# class Event(FlaskForm):
#     eventName = StringField('Event Name', validators = [DataRequired()])
#     date = DateField('Date', format="%Y-%m-%d", validators = [DataRequired()])
#     location = StringField('location', validators = [DataRequired()])
#     eventCoordinater = StringField('Email', validators = [DataRequired(), Email()])
#     submit = SubmitField('Create Event')

# class AddEventItem(FlaskForm):
#     eventName = SelectField('Event', coerce=str, validators=[DataRequired()])
#     item = StringField('Item', validators = [DataRequired()])
#     availableSlots = IntegerField('Number of Slots')
#     submit = SubmitField('Create Item')
    
# class eventSignup(FlaskForm):
#     item = SelectField('AddEventItem', coerce=str, validators=[DataRequired()])
#     dishName = StringField('Dish Name', validators = [DataRequired()])
#     comments = StringField('Comments')
#     dairy = BooleanField('Dairy', default = False)
#     gluten = BooleanField('Gluten', default = False)
#     meat = BooleanField('Meat', default = False)
#     eggs = BooleanField('Eggs', default = False)
#     fish = BooleanField('Fish', default = False)
#     nuts = BooleanField('Nuts', default = False)
    
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# import email_validator

# class RegisterForm(FlaskForm):
#     email = StringField('Email', validators= [DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo(password)])
#     code = PasswordField("Admin Code", validators=[EqualTo("1234")])
#     submit = SubmitField('Register')
    

# class LoginForm(FlaskForm):
#     email = StringField('Email', validators= [DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     submit = SubmitField('Sign In')