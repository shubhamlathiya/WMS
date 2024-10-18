from datetime import datetime

from bson import ObjectId
from flask import Blueprint, render_template, request, jsonify, redirect, session
from config import mongo

from email_utils import send_email
from middleware.auth_middleware import token_required
from api.client_routes.client_dashboard_routes import client

from . import client

# client add
@client.route('/dashboard', methods=['GET'], endpoint='orderProducts')
@token_required
# @role_required('order_routes')
def order_products(current_user):
    try:
        products = mongo.db.products.find()
        # print(list(products))
        product_list = []
        for product in products:
            stock_record = mongo.db.stock.find({'sku': product['sku']}).sort('date', -1).limit(1)

            stock_record = list(stock_record)

            if stock_record:
                stock_qty = stock_record[0]['total_qty']
            else:
                stock_qty = 0

            product_list.append({
                'image': product['image'],
                'name': product['product_name'],
                'sku': product['sku'],
                'price': product['price'],
                'stock_qty': stock_qty
            })
        print(product_list)
        return render_template("client/client_dashboard.html", products=product_list)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@client.route('/submitOrder', methods=['POST'], endpoint='submitOrder')
@token_required
def submit_order(current_user):
    try:

        order_details = request.json  # Expecting JSON data
        print(order_details)
        total_amount = float(order_details['totalAmount'])  # Parse the total amount
        payment_type = order_details['paymentType']  # Payment type (Cash, Razorpay, etc.)
        ordered_products = []

        # Iterate through each product in the order_routes
        for product in order_details['products']:
            product_id = product['id']
            quantity = int(product['qty'])  # Quantity ordered

            # Find the product by SKU in the database
            product_record = mongo.db.products.find_one({'sku': int(product_id)})
            if not product_record:
                return jsonify({'status': 'error', 'message': f"Product with SKU {product_id} not found."}), 400

            # Fetch the latest stock record for the product
            stock_record = mongo.db.stock.find_one({'sku': product_record['sku']}, sort=[('date', -1)])
            if not stock_record or stock_record['total_qty'] < quantity:
                return jsonify({'status': 'error', 'message': f"Not enough stock for {product_record['name']}"}), 400

            # Update stock and create a new stock record
            new_total_qty = stock_record['total_qty'] - quantity
            new_stock_entry = {
                "sku": product_record['sku'],
                "date": datetime.now(),
                "+qty": 0,
                "-qty": quantity,
                "total_qty": new_total_qty
            }

            # Insert new stock record into the stock collection
            new_stock_record = mongo.db.stock.insert_one(new_stock_entry)

            print(new_stock_record)
            # Append product to the ordered products list
            ordered_products.append({
                'product_id': str(product_record['_id']),  # Convert ObjectId to string
                'product_name': product_record['product_name'],
                'quantity': quantity,
                'price': product_record['price'],
                'amount': product_record['price'] * quantity,
                'stock_record_id': str(new_stock_record.inserted_id)  # Track the stock record ID
            })

        # Create the order_routes object
        order = {
            'user_id': ObjectId(session['user_id']),  # Replace with `current_user` if available
            'products': ordered_products,
            'total_amount': total_amount,
            'status': 'submitted',
            'payment_type': payment_type,
            'order_date': datetime.now()
        }

        # Insert the order_routes into the orders collection
        order_new = mongo.db.orders.insert_one(order)
        print(order_new)
        # Handle payment processing
        if payment_type == 'Cash':
            transaction_status = 'pending'
        else:
            transaction_status = 'completed'

        transaction = {
            'order_id': ObjectId(str(order_new.inserted_id)),  # Convert ObjectId to string
            'amount': total_amount,
            'payment_type': payment_type,
            'payment_status': transaction_status,  # 'completed' for cash, 'pending' for online
            'transaction_date': datetime.now()
        }

        mongo.db.transactions.insert_one(transaction)

        assigned_employee = assign_order_to_employee(order_new.inserted_id)

            # Send email to the client with order details
        client_email = session['email']  # Assuming the user's email is in `current_user`
        send_order_confirmation_email(client_email, order, ordered_products)

        return jsonify(
            {'status': 'success', 'message': 'Order placed successfully', 'order_id': str(order_new.inserted_id),
             'url': "/client/dashboard"}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def assign_order_to_employee(order_id):
    # Fetch the queue of employees who have role "employee" and status "true"
    employees = list(mongo.db.users.find(
        {'role': 'employee', 'status': 'true'}))  # Assuming the role and status are in 'users' collection
    if not employees:
        return None

    # Fetch the current queue pointer (index of the last assigned employee)
    queue_data = mongo.db.queue.find_one({})  # Assuming the queue information is stored in a 'queue' collection

    if not queue_data:
        # If no queue data exists, initialize it with the first employee
        queue_data = {
            'current_employee_index': 0
        }
        mongo.db.queue.insert_one(queue_data)

    # Get the current employee index
    current_employee_index = queue_data['current_employee_index']

    # Find the next employee in the queue
    next_employee_index = (current_employee_index + 1) % len(employees)  # Round-robin logic

    # Assign the next employee
    assigned_employee = employees[next_employee_index]

    # Update the queue pointer to the new employee
    mongo.db.queue.update_one({}, {'$set': {'current_employee_index': next_employee_index}})

    # Create an assignment record in the 'assignments' collection
    assignment = {
        'order_id': ObjectId(order_id),
        'employee_id': assigned_employee['_id'],
        'assigned_date': datetime.now(),
        'status': 'assigned'
    }
    mongo.db.assigned_tasks.insert_one(assignment)

    return assigned_employee

def send_order_confirmation_email(email, order, products):
    try:
        product_details = "\n".join(
            [f"{p['product_name']} - {p['quantity']} x {p['price']} = {p['amount']}" for p in products]
        )

        msg_body = f"""
        Hello,

        Thank you for your order!

        Order Details:
        Order ID: {str(order['_id'])}
        Total Amount: {order['total_amount']}
        Payment Type: {order['payment_type']}
        Order Date: {order['order_date'].strftime('%Y-%m-%d')}

        Products:
        {product_details}

        Regards,
        Your Company Name
        """

        subject="Order Confirmation"

        send_email(subject, email, msg_body)

        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {str(e)}")