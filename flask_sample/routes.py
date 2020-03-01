import secrets, os
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from flask_sample import app, db, bcrypt, mail
from flask_sample.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
								PostForm, ResetRequestForm, ResetPasswordForm)
from flask_sample.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
''' Take note this functions variables login_user, current_user, 
logout_user are available outside of this module or in views. 
It is accessible via template (eg; register.html)'''


@app.route('/')
@app.route('/home')
def home_page():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate( page=page, per_page=5)
	return render_template('home.html', title = 'Homepage', posts = posts )


@app.route('/about')
def about():
	return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():

	if current_user.is_authenticated:
		return redirect(url_for('home_page'))

	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Account has been created for {form.username.data}!', category='success') # One time alert
		return redirect(url_for('home_page'))

	return render_template('register.html', title='Register', form = form)


@app.route('/login', methods=['GET', 'POST'])
def login():

	#Check if the user is logged in
	if current_user.is_authenticated:
		return redirect(url_for('home_page'))

	form = LoginForm()
	# Authenticate User
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next') # Access query parameter 
			return redirect(next_page) if next_page else redirect(url_for('home_page')) # Ternary Conditional
		else:
			flash('Login Unsuccessful. Please check email or password.', category='danger')

	return render_template('login.html', title='Login', form = form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))


def photo_save(form_photo): # Use to resize and rename profile pictures.
	random = secrets.token_hex(8)
	_, fext = os.path.splitext(form_photo.filename)
	fname = random + fext
	photopath = os.path.join(app.root_path, 'static/profile', fname)

	output_size = 125, 125

	img = Image.open(form_photo)
	img.thumbnail(output_size)
	img.save(photopath)

	return fname


@app.route('/account', methods=['GET', 'POST'])
@login_required # Restricted route which requires users to login.
def account():
	form = UpdateAccountForm()

	if form.validate_on_submit():
		#check_user = User.query.filter_by(username=form.username.data).first()
		if form.photo.data:
			user_photo = photo_save(form.photo.data)
			current_user.image_file = user_photo
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your profile has been successfully updated!', 'success')
		return redirect(url_for('account'))

	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	image_file = url_for('static', filename='profile/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form = form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required # Restricted route which requires users to login.
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author = current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been successfully created!', 'success')
		return redirect(url_for('home_page'))
	return render_template('create_post.html', title='Create Post',
							form = form, legend='New Post')


@app.route('/post/<int:post_id>')
@login_required # Restricted route which requires users to login.
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post = post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required # Restricted route which requires users to login.
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('post', post_id=post_id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Create Post',
							form = form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required # Restricted route which requires users to login.
def delete_post(post_id):
	form = PostForm()
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)

	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted successfully!', 'success')
	return redirect(url_for('home_page'))


@app.route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user)\
			.order_by(Post.date_posted.desc())\
			.paginate(page=page, per_page=5)
	return render_template('user_posts.html', title = 'Posts', posts = posts, user=user )


def send_reset(user):
	token = user.get_reset_token(	)
	msg = Message('Request for Password Reset',
					sender='noreply@demo.com',
					recipients=[user.email])
	msg.body = f''' To reset your password, visit the ff. link:
	{url_for('reset_token', token=token, _external=True)}

If you did not make this request simply ignore or delete this mail.
'''
	mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home_page'))
	form = ResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset(user)
		flash('An e-mail has been sent for password reset.')
		return redirect(url_for('login'))
	return render_template('request_reset.html', title = 'Reset Password', form = form )


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home_page'))
	user = User.validate_reset_token(token)
	if user is None:
		flash('Invalid link. It\'s either the token was expired or invalid.', 'warning')
		return redirect(url_for('reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated!', 'info')
		return redirect(url_for('home_page'))
	return render_template('password_reset.html', title= 'Reset Password', form = form )

