from flask import Blueprint, render_template, url_for, flash, redirect, request
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash

from config import mongo
from email_utils import send_email

forgotpassword = Blueprint('forgotpassword', __name__)

s = URLSafeTimedSerializer("SECRET_KEY")


@forgotpassword.route('/', methods=['GET'])
def forgot_password():
    return render_template('auth/forgetpassword.html')


@forgotpassword.route('/reset', methods=['POST'])
def reset_password():
    try:
        email = request.form.get('email')
        print(email)
        user = mongo.db.users.find_one({'email': email})
        print(user)
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            # print(token)  # Generate token
            base_url = "http://127.0.0.1:5000/forgotpassword/"
            reset_link = f"{base_url}/reset-password/{token}"
            # print(reset_link)
            subject = "Password Reset Request"
            # Send email with reset link
            send_email(subject, email, reset_link)

            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('Email not found', 'danger')
        return redirect('/')

    except Exception as e:
        return redirect('/forgotpassword')


#
@forgotpassword.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_home(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=1800)  # Token expires in 30 minutes
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        # Hash the password before storing
        hashed_password = generate_password_hash(new_password)  # Implement password hashing
        # Update the user's password in the database
        mongo.db.users.update_one(
            {'email': email},
            {
                '$set': {
                    'password': hashed_password,
                }
            }
        )
        flash('Your password has been updated.', 'success')
        return redirect('/')

    return render_template('auth/reset_password.html')
