from bson import ObjectId
from flask import Flask, request, jsonify, render_template, Blueprint, redirect
from werkzeug.security import generate_password_hash
from config import mongo
from email_utils import send_email
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

user = Blueprint('user', __name__)


@user.route('/adduser')
@token_required
@role_required('users', 'create')
def add_user(current_user):
    return render_template("user/add_user.html")


@user.route('/updateuser/<string:user_id>', methods=['GET'], endpoint='update_user_home')
@token_required
@role_required('users', 'edit')
def update_user_home(current_user, user_id):
    # print("user_id")
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    return render_template("user/update_user.html", user=user)

@user.route('/viewuser', methods=['GET'], endpoint='viewuser')
@token_required
@role_required('users', 'view')
def view_user(current_user):
    try:
        users_list = list(mongo.db.users.find({'role': {'$in': ['manager', 'employee', 'admin']}}))
        return render_template("user/view_user.html", users_list=users_list)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@user.route('/adduser', methods=['POST'], endpoint='adduser')
@token_required
@role_required('users', 'create')
def add_personnel(current_user):
    try:
        data = request.json
        name = data.get('full_name')
        uname = data.get('user_name')
        mobile = data.get('mobile')
        email = data.get('email')
        password = generate_password_hash(data.get('password'))
        role = data.get('role')

        print("hy")
        if not name or not mobile or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        # Create a personnel document
        personnel = {
            'full_name': name,
            'user_name': uname,
            'mobile': mobile,
            'email': email,
            'password': password,  # Store the hashed password
            'role': role,
            'status': "true"
        }

        # Insert into MongoDB
        mongo.db.users.insert_one(personnel)

        # Prepare email details
        subject = 'Employee Details'
        body = f"""
               Dear {name},

               Your details have been successfully registered.

               Mobile: {mobile}
               Role: {role}
               Password: {data.get('password')} (Remember to change it after logging in)
               """

        # Send email
        if send_email(subject, email, body):
            return jsonify({"message": "Personnel added and email sent!"}), 200
        else:
            return jsonify({"error": "Failed to send email."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user.route('/updateuser/<string:user_id>', methods=['POST'], endpoint='update_user')
@token_required
@role_required('users', 'edit')
def update_user(current_user, user_id):
    try:
        # print(user_id)
        name = request.form.get('full_name')
        uname = request.form.get('user_name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        role = request.form.get('role')

        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'full_name': name,
                    'user_name': uname,
                    'mobile': mobile,
                    'email': email,
                    'role': role,
                }
            }
        )

        return redirect('/user/viewuser')

    except Exception as e:
        # flash(f"Error updating user: {str(e)}", 'error')
        return redirect('/user/viewuser')

@user.route('/user_status', methods=['POST'])
def user_status():
    data = request.get_json()

    user_id = data.get('user_id')  # User ID passed from the client-side
    new_status = data.get('status')  # New status (true/false)

    if user_id and new_status:
        # Update the user's status in the database
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'status': new_status}}
        )

        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Status updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Status update failed'})
    return jsonify({'success': False, 'message': 'Invalid request'}), 400

@user.route('/viewclient', methods=['GET'], endpoint='viewclient')
@token_required
@role_required('users', 'view')
def view_client(current_user):
    try:
        users_list = list(mongo.db.users.find({'role': 'client'}))
        return render_template("user/view_client.html", users_list=users_list)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@user.route('/viewsupplier', methods=['GET'], endpoint='viewsupplier')
@token_required
@role_required('users', 'view')
def supplier_client(current_user):
    try:
        users_list = list(mongo.db.users.find({'role': 'supplier'}))
        return render_template("user/view_supplier.html", users_list=users_list)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500