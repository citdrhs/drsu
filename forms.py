from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegisterForm(FlaskForm):
    username = StringField('Username', validators= [DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
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