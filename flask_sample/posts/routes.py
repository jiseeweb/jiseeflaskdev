from flask import render_template, flash, redirect, url_for, request, abort, Blueprint
from flask_sample import db
from flask_sample.posts.forms import PostForm
from flask_login import login_user, current_user, login_required
from flask_sample.models import User, Post

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required # Restricted route which requires users to login.
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author = current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been successfully created!', 'success')
		return redirect(url_for('main.home_page'))
	return render_template('create_post.html', title='Create Post',
							form = form, legend='New Post')


@posts.route('/post/<int:post_id>')
@login_required # Restricted route which requires users to login.
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post = post)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
		return redirect(url_for('posts.post', post_id=post_id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Create Post',
							form = form, legend='Update Post')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required # Restricted route which requires users to login.
def delete_post(post_id):
	form = PostForm()
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)

	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted successfully!', 'success')
	return redirect(url_for('main.home_page'))
