from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_sample.models import User
from flask_login import current_user
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=3, max=12)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign up')

	# Custom Validation Autocalled?
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username already exist. Please choose another one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('E-mail already exist. Please choose another one.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=4, max=12)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	photo = FileField('Profile Photo', validators=[FileAllowed(['png', 'jpg'])])
	submit = SubmitField('Update')

	# Custom Validation Autocalled? YES
	def validate_username(self, username):
		if current_user.username != username.data:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username already exist. Please choose another one.')

	def validate_email(self, email):
		if current_user.email != email.data:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('E-mail already exist. Please choose another one.')


class PostForm(FlaskForm):

	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Post')


class ResetRequestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Send Request')


	def validate_email(self, email):
		#if current_user.email != email.data:
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('E-mail doesn\'t exist. Create an account instead.')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Change Password')
