from flask import Flask, request, jsonify, render_template, Blueprint , session
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

from config import mongo
from bson.objectid import ObjectId

employee = Blueprint('employee', __name__)


@employee.route('/dashboard', methods=['GET'])
@token_required
@role_required('employee_dashboard', 'view')
def dashboard_home(current_user):
    try:
        assigned_tasks = list(mongo.db.assigned_tasks.aggregate([
            {
                '$match': {
                    'employee_id': ObjectId(session['user_id']),  # Match the employee_id
                }
            },
            {
                '$lookup': {
                    'from': 'orders',  # Join with the orders collection
                    'localField': 'order_id',  # Field in assignments collection
                    'foreignField': '_id',  # Field in orders collection
                    'as': 'order_details'
                }
            },
            {
                '$unwind': '$order_details'  # Unwind the order details array
            },
            {
                '$lookup': {
                    'from': 'users',  # Join with the users collection
                    'localField': 'order_details.user_id',  # Field in order details
                    'foreignField': '_id',  # Field in users collection
                    'as': 'user_details'
                }
            },
            {
                '$unwind': '$user_details'  # Unwind the user details array
            },
            {
                '$unwind': '$order_details.products'  # Unwind products
            },
            {
                '$addFields': {
                    'order_details.products.product_id': {
                        '$convert': {
                            'input': '$order_details.products.product_id',
                            'to': 'objectId',
                            'onError': None  # Avoid conversion failures
                        }
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'products',  # Join with the products collection
                    'localField': 'order_details.products.product_id',  # Field in order details products
                    'foreignField': '_id',  # Field in products collection
                    'as': 'product_details'
                }
            },
            {
                '$unwind': '$product_details'  # Unwind the product details array
            },
            {
                '$lookup': {
                    'from': 'areas',  # Join with the areas collection
                    'localField': 'product_details.area_id',  # Field in products collection (area_id)
                    'foreignField': '_id',  # Field in areas collection
                    'as': 'area_details'
                }
            },
            {
                '$unwind': '$area_details'  # Unwind the area details array
            },
            {
                '$group': {
                    '_id': {
                        'assignment_id': '$_id',
                        'order_id': '$order_id',
                        'employee_id': '$employee_id',
                        'assigned_date': '$assigned_date',
                        'status': '$status',
                        'order_details': '$order_details._id',
                        'user_id': '$order_details.user_id',
                        'user_full_name': '$user_details.full_name'
                    },
                    'products': {
                        '$push': {
                            'product_id': '$order_details.products.product_id',
                            'product_name': '$order_details.products.product_name',
                            'quantity': '$order_details.products.quantity',
                            'price': '$order_details.products.price',
                            'area_name': '$area_details.area_name'
                        }
                    }
                }
            },
            {
                '$sort': {
                    'assigned_date': -1  # Sort by assigned_date in descending order
                }
            },
            {
                '$project': {
                    '_id': 0,  # Hide the default _id from the output
                    'assignment_id': '$_id.assignment_id',
                    'order_id': '$_id.order_id',
                    'employee_id': '$_id.employee_id',
                    'assigned_date': '$_id.assigned_date',
                    'status': '$_id.status',
                    'order_details._id': '$_id.order_details',
                    'order_details.user_id': '$_id.user_id',
                    'products': 1,  # Output the array of products
                    'user_details.full_name': '$_id.user_full_name'
                }
            }
        ]))

        # print(assigned_tasks[0].user_details.full_name)
        # print(assigned_tasks)
        return render_template('dashboard/employee_dashboard.html', assigned_tasks=assigned_tasks)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


    # return render_template('dashboard/employee_dashboard.html')


@employee.route('/update/<order_id>', methods=['POST'], endpoint='update')
@token_required
def update_order_status(current_user, order_id):
    try:
        print(f"updated : {order_id}")
        # Assigned , Shipment Ready,Out for Delivery,Delivered,Cancelled
        mongo.db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': 'Shipment Ready'}})
        mongo.db.assigned_tasks.update_one({'order_id': ObjectId(order_id)}, {'$set': {'status': 'Shipment Ready'}})
        return jsonify({'status': 'success', 'message': 'Order status updated successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
