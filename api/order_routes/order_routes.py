from flask import Blueprint, render_template, request, jsonify, redirect, session
from config import mongo
from middleware.auth_middleware import token_required

# Initialize blueprint
order = Blueprint('order', __name__)


@order.route('/order', methods=['GET'], endpoint='order')
@token_required
def order_home(current_user):
    return render_template('order/orders.html')


@order.route('/getorders', methods=['GET'], endpoint='getorders')
@token_required
# @role_required('order_routes')
def get_orders(current_user):
    try:
        # Fetch all orders from the database
        all_orders = mongo.db.orders.find()

        orders_list = []
        for order in all_orders:
            # Create an order_routes dictionary with basic order_routes info
            order_dict = {
                'order_id': str(order['_id']),
                'user_id': order['user_id'],  # Add user info if needed
                'total_amount': order['total_amount'],
                'status': order['status'],
                'order_date': order['order_date'].strftime('%Y-%m-%d'),
                'products': []  # List of products in the order_routes
            }

            # Add products details to the order_routes
            for product in order['products']:
                product_info = {
                    'product_name': product['product_name'],
                    'quantity': product['quantity'],
                    'price': product['price'],
                    'amount': product['amount']
                }
                order_dict['products'].append(product_info)

            orders_list.append(order_dict)

        return jsonify({'status': 'success', 'orders': orders_list}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@order.route('/packages', methods=['GET'])
@token_required
def get_all_packages(current_user):
    try:
        # Assigned , Shipment Ready,Out for Delivery,Delivered,Cancelled
        not_shipped_packages = list(mongo.db.orders.aggregate([
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user_info'
                }
            },
            {
                '$match': {'Delivered_status': 'Not Shipped'}
            }
        ]))

        shipped_packages = list(mongo.db.orders.aggregate([
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user_info'
                }
            },
            {
                '$match': {'Delivered_status': 'Shipped'}
            }
        ]))

        delivered_packages = list(mongo.db.orders.aggregate([
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user_info'
                }
            },
            {
                '$match': {'Delivered_status': 'Delivered'}
            }
        ]))

        # Render template with grouped packages
        return render_template(
            'order/packages.html',
            not_shipped=not_shipped_packages,
            shipped=shipped_packages,
            delivered=delivered_packages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
