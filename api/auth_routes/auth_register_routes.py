import random
from flask import Blueprint, request, jsonify, render_template, session, redirect
from werkzeug.security import generate_password_hash

from config import mongo
from email_utils import send_email

register = Blueprint('register', __name__)


@register.route('/', methods=['POST'])
def register_user():
    # data = request.get_json()
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')

    user = mongo.db.users.find_one({'email': email})
    #
    if user:
        return jsonify({'message': 'User already exists!'}), 400

    otp = random.randint(1000, 9999)

    # Save OTP in session temporarily
    session['otp'] = otp
    session['full_name'] = full_name
    session['email'] = email
    session['password'] = password

    subject = "Your OTP for Registration"
    body = f"Your OTP is {otp}. Please enter this to complete your registration."
    send_email(subject, email, body)

    # print(full_name, email, password)
    # user = mongo.db.users.find_one({'email': data['email']})
    #
    # if user:
    #     return jsonify({'message': 'User already exists!'}), 400
    #
    # user_id = mongo.db.users.insert_one({
    #     'email': data['email'],
    #     'password': data['password']  # Hash this in production
    # }).inserted_id

    # return jsonify({'message': 'User registered successfully!'})
    return redirect('/register/verify-otp')


@register.route('/', methods=['GET'])
def register_user2():
    return render_template('auth/signup.html')


# OTP Verification Page
@register.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        # Check if the OTP matches
        if 'otp' in session and int(entered_otp) == session['otp']:
            # OTP matched, save user to the database
            user_data = {
                'full_name': session['full_name'],
                'email': session['email'],
                'password': generate_password_hash(session['password']),
                'role': "client",
                'status': "true"
            }

            # Insert the user data into MongoDB
            mongo.db.users.insert_one(user_data)

            # Clear session data
            session.pop('otp', None)
            session.pop('full_name', None)
            session.pop('email', None)
            session.pop('password', None)

            return redirect('/')
        else:
            return jsonify({'error': 'Invalid OTP'}), 400

    return render_template('auth/otp.html')
