import secrets, os
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flask_sample import mail

def photo_save(form_photo): # Use to resize and rename profile pictures.
	random = secrets.token_hex(8)
	_, fext = os.path.splitext(form_photo.filename)
	fname = random + fext
	photopath = os.path.join(current_app.root_path, 'static/profile', fname)

	output_size = 125, 125

	img = Image.open(form_photo)
	img.thumbnail(output_size)
	img.save(photopath)

	return fname


def send_reset(user):
	token = user.get_reset_token(	)
	msg = Message('Request for Password Reset',
					sender='noreply@demo.com',
					recipients=[user.email])
	msg.body = f''' To reset your password, visit the ff. link:
	{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request simply ignore or delete this mail.
'''
	mail.send(msg)