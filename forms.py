from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange

class RegisterForm(FlaskForm):
    #username = StringField('Username', validators= [DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    first_name = StringField('FirstName', validators = [DataRequired()])
    last_name = StringField('LastName', validators = [DataRequired()])
    grade = SelectField('Grade', choices=[('8', '8'),('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], coerce=int)
    password = PasswordField('Password', validators = [DataRequired()])
    is_admin = BooleanField(default=False)
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    adminCode = IntegerField('Admin Code')
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
