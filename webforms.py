from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

#Create a Search Form
class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")

#create login form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

#Create A Post Form
class  AskForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	file = FileField("Upload Image : ", validators=[DataRequired()])
	content = CKEditorField('Content', validators=[DataRequired()])
	author = StringField("Author")
	slug = StringField("Summary", validators=[DataRequired()])
	submit = SubmitField("Submit")

#Create A Post Form
class  PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	file = FileField("Upload Image : ", validators=[DataRequired()])
	content = CKEditorField('Content', validators=[DataRequired()])
	author = StringField("Author")
	slug = StringField("Summary", validators=[DataRequired()])
	submit = SubmitField("Submit")

#create a userform class
class UserForm(FlaskForm):
	name = StringField("Name :", validators=[DataRequired()])
	username = StringField("(Note: User your Email as Your User Name) Username :", validators=[DataRequired()])
	email = StringField("Email Address :", validators=[DataRequired()])
	about_author = TextAreaField("About : ")
	password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
	profile_pic = FileField("Profile Pic : ")
	submit = SubmitField("Submit")

#create a Password class
class PasswordForm(FlaskForm):
	email = StringField("what's your Email", validators=[DataRequired()])
	password_hash = PasswordField("what's your Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

#create a form class
class NamerForm(FlaskForm):
	name = StringField("what's your name", validators=[DataRequired()])
	submit = SubmitField("Submit")
