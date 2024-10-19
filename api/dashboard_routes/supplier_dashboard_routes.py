from datetime import datetime
from random import randint

from bson import ObjectId
from flask import Flask, request, jsonify, render_template, Blueprint, redirect, session

from api.order_routes.order_routes import order
from config import mongo
from email_utils import send_email
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

supplier = Blueprint('supplier', __name__)


@supplier.route('/dashboard', methods=['GET'], endpoint='supplier_orders')
@token_required
def get_supplier_orders(current_user):
    try:
        # print(f"Fetching orders for supplier: {session['user_id']}")

        # Fetch assigned tasks for the supplier
        assigned_tasks = list(mongo.db.assigned_tasks.find({
            'supplier_id': ObjectId(session['user_id']),
            'status':"Assigned to Supplier"
        }))

        if not assigned_tasks:
            return jsonify({'status': 'error', 'message': 'No orders assigned to this supplier.'}), 404

        # Create a list to hold orders details
        orders_details = []
        for task in assigned_tasks:
            # Ensure order_id is an ObjectId before querying
            order_id = task.get('order_id')
            if not order_id:
                continue  # Skip if there's no order_id

            # Fetch the corresponding order details using the order_id
            order = mongo.db.orders.find_one({'_id': order_id})
            if order:
                # Fetch the user details using user_id from the order
                user_id = order.get('user_id')
                user = mongo.db.users.find_one({'_id': ObjectId(user_id)})

                # If user is found, extract details
                user_details = {}
                if user:
                    user_details = {
                        'name': user.get('full_name', ''),
                        'mobile': user.get('mobile', ''),
                        'city': user.get('city', ''),
                        'area': user.get('area', '')
                    }

                # Build the order detail object including user details
                order_detail = {
                    'order_id': str(order['_id']),
                    'products': order.get('products', []),  # Use get to avoid KeyError
                    'total_amount': order.get('total_amount', 0),
                    'payment_type': order.get('payment_type', ''),
                    'order_date': order.get('order_date', None),
                    'status': order.get('status', [])[-1]['status'] if order.get('status', []) else '',
                    'user_details': user_details  # Include the user details
                }
                orders_details.append(order_detail)

        # return jsonify({'status': 'success', 'orders': orders_details}), 200
        return render_template('dashboard/supplier.html', orders_details=orders_details)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@supplier.route('/pickup', methods=['POST'], endpoint='pickup')
@token_required
def pickup_multiple_orders(current_user):
    try:
        # print("1")
        # print(request.form)
        # Get the list of order IDs from the form
        order_ids = request.form.getlist('order_ids')

        # Check if any order is selected
        if not order_ids:
            return jsonify({'status': 'error', 'message': 'No orders selected for pickup.'}), 400

        for order_id in order_ids:
            # Step 1: Update each order status to 'Out for Delivery'
            # mongo.db.orders.update_one(
            #     {'_id': ObjectId(order_id), 'assigned_supplier_id': ObjectId(current_user['_id'])},
            #     {'$set': {'status': 'Out for Delivery', 'pickup_date': datetime.now()}}
            # )

            mongo.db.orders.update_one(
                {'_id': ObjectId(order_id)},
                {'$push': {
                    'status': {
                        'status': 'Out for Delivery',
                        'updated_at': datetime.now()
                    }
                }}
            )

            mongo.db.assigned_tasks.update_one(
                {'order_id': ObjectId(order_id)},
                {
                    '$set': {
                        'status': 'Out for Delivery'  # Update the current status
                    }
                }
            )

            # Step 2: Generate an OTP and update the order
            otp = randint(100000, 999999)
            mongo.db.orders.update_one(
                {'_id': ObjectId(order_id)},
                {'$set': {'otp': otp}}
            )

            # Step 3: Send OTP to the customer via email or SMS (assuming email here)
            order = mongo.db.orders.find_one({'_id': ObjectId(order_id)})
            client = mongo.db.users.find_one({'_id': ObjectId(order['user_id'])})
            body = str(otp)  # You need to implement this function

            subject = "Order Confirmation OTP"

            send_email(subject, client['email'], body)

        return redirect('/supplier/dashboard')
        # return jsonify({'status': 'success', 'message': 'Orders picked up and OTP sent to customers.'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@supplier.route('/deliver/<order_id>', methods=['POST'], endpoint='deliver')
@token_required
def deliver_order(current_user, order_id):
    try:
        print("deliver" , order_id)
        otp_entered = request.form.get('otp')
        cash_collected = request.form.get('cash_collected')  # For COD orders


        # Fetch the order from the database
        order = mongo.db.orders.find_one({'_id': ObjectId(order_id)})

        # Verify OTP
        if otp_entered != str(order['otp']):
            return jsonify({'status': 'error', 'message': 'Invalid OTP'}), 400


        # If the order is COD, ensure cash is collected
        if order['payment_type'] == 'Cash' and not cash_collected:
            return jsonify({'status': 'error', 'message': 'Cash not collected for COD order'}), 400

        # Mark the order as delivered
        # mongo.db.orders.update_one({'_id': ObjectId(order_id)},
        #                            {"$set": {'status': 'Delivered', 'delivery_date': datetime.now()}})


        mongo.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$push': {
                'status': {
                    'status': 'Delivered',
                    'delivery_date': datetime.now()
                }
            }}
        )


        mongo.db.assigned_tasks.update_one(
            {'order_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': 'Delivered'  # Update the current status
                }
            }
        )



        # Insert cash collection record for WMS manager if COD
        if order['payment_type'] == 'Cash':
            cash_entry = {
                'order_id': ObjectId(order_id),
                'collected_by_supplier_id': ObjectId(session['user_id']),
                'amount': int(order['total_amount']),
                'submission_date': datetime.now()
            }
            mongo.db.cash_collections.insert_one(cash_entry)

        # print("cash")

        return redirect('/supplier/dashboard')

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

#
# # Route to submit cash to WMS manager
# @supplier.route('/submit_cash/<cash_id>', methods=['POST'])
# @token_required
# @role_required('supplier', 'edit')
# def submit_cash(current_user, cash_id):
#     try:
#         # Mark the cash as submitted to WMS manager
#         mongo.db.cash_collections.update_one({'_id': ObjectId(cash_id)}, {"$set": {'submission_date': datetime.now()}})
#         return jsonify({'status': 'success', 'message': 'Cash submitted to WMS manager'}), 200
#
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500
