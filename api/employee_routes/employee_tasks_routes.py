from flask import Blueprint, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from config import mongo
from middleware.auth_middleware import token_required

tasks = Blueprint('tasks', __name__)


@tasks.route('/tasks', methods=['GET'])
@token_required
def show_assigned_tasks(current_user):
    try:
        print(session['user_id'])
        assigned_tasks = list(mongo.db.assignments.aggregate([
            {
                '$lookup': {
                    'from': 'orders',  # Join with the orders collection
                    'localField': 'order_id',  # Field in assignments collection
                    'foreignField': '_id',  # Field in orders collection
                    'as': 'order_details'  # Resulting array of order details
                }
            },
            {
                '$unwind': '$order_details'  # Unwind the order details array to make it easier to work with
            },
            {
                '$lookup': {
                    'from': 'users',  # Join with the users collection
                    'localField': 'order_details.user_id',  # Field in order details
                    'foreignField': '_id',  # Field in users collection
                    'as': 'user_details'  # Resulting array of user details
                }
            },
            {
                '$unwind': '$user_details'  # Unwind the user details array
            },
            {
                '$project': {
                    'user_details.full_name': 1,  # Only fetch the full_name from the users collection
                    'employee_id': 1,
                    'order_id': 1,
                    'order_details': 1,
                    'assigned_date': 1,
                    'status': 1
                }
            },
            {
                '$match': {
                    'employee_id': ObjectId(session['user_id']),  # Only fetch tasks for the logged-in employee
                    'status': 'assigned'  # Only fetch tasks with 'assigned' status
                }
            }
        ]))

        # print(assigned_tasks[0].user_details.full_name)
        print(assigned_tasks)
        return render_template('client/../../templates/employee/tasks.html', assigned_tasks=assigned_tasks)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# @tasks.route('/tasks/update/<order_id>', methods=['POST'], endpoint='update')
# @token_required
# def update_order_status(current_user, order_id):
#     try:
#         mongo.db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': 'completed'}})
#         return jsonify({'status': 'success', 'message': 'Order status updated successfully.'}), 200
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500
