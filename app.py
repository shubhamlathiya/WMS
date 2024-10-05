import subprocess

from api.products_routes.area_routes import area
# from apscheduler.schedulers.background import BackgroundScheduler
from config import init_app
from api.auth_routes.auth_login_routes import login
from api.auth_routes.forgot_password_routes import forgotpassword
from api.auth_routes.auth_register_routes import register
from api.products_routes.products_routes import product
from api.dashboard_routes.admin_dashboard_routes import admin
from api.stock_routes.stock_routes import stock
from api.user_routes.user_routes import user
from api.order_routes.order_routes import order
from api.page_visibility_routes.page_visibility import settings
from api.employee_routes.employee_tasks_routes import tasks
from api.client_routes.client_order_routes import client
from flask import Flask, render_template, jsonify
import winsound
from flask_mail import Mail

app = Flask(__name__)
# crontab = Crontab(app)
# Initialize MongoDB
init_app(app)

# Set a secret key for the session
app.config['SECRET_KEY'] = 'your_secure_random_key'
# Register blueprints (routes)
app.register_blueprint(login, url_prefix='/login')
app.register_blueprint(area, url_prefix='/area')
app.register_blueprint(forgotpassword, url_prefix='/forgotpassword')
app.register_blueprint(register, url_prefix='/register')
app.register_blueprint(admin, url_prefix='/dashboard')

app.register_blueprint(product, url_prefix='/product')
app.register_blueprint(order, url_prefix='/order')
app.register_blueprint(stock, url_prefix='/stock')
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(settings, url_prefix='/settings')
app.register_blueprint(tasks, url_prefix='/tasks')
app.register_blueprint(client, url_prefix='/client')
# A protected route using token authentication

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'shubhamlathiya2021@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'tqerujnjzuvgdjho'  # Your email password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Initialize the mail object
mail = Mail(app)


@app.route('/')
def home():
    return render_template("auth/signin.html")


@app.route('/logout', methods=['GET'])
def logout():
    response = jsonify({'message': 'Logged out successfully!'})
    response.set_cookie('token', '', expires=0)  # Clear the cookie
    return response


def play_beep():
    frequency = 1000  # Set Frequency To 1000 Hertz
    duration = 500  # Set Duration To 500 ms (0.5 seconds)
    winsound.Beep(frequency, duration)


@app.errorhandler(404)
def handle_404_error(e):
    return render_template('error_handler/error_404.html')
    # return jsonify({'status': 'error shubham', 'message': 'Resource not found (404)'}), 404


@app.errorhandler(500)
def handle_500_error(e):
    return render_template('error_handler/error_500.html')
    # return jsonify({'status': 'error', 'message': 'Internal server error (500)'}), 500


@app.route('/scan', methods=['GET'])
def scan():
    try:
        print("hy")
        # Run the qr.py script and capture its output
        result = subprocess.run(['python', 'qr.py'], capture_output=True, text=True)
        output = result.stdout.strip()  # Get the output from qr.py

        # Return the result as JSON
        return jsonify({'barcode': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# def monitor_stock_levels():
#     print("Scheduler started.")
#     # while True:
#     products = mongo.db.products.find({})
#     print(products)
#     for product in products:
#     # Fetch the latest stock entry for this product
#         stock_record = mongo.db.stock.find_one(
#             {'sku': product['sku']}, sort=[('date', -1)]
#             )
#         print(stock_record)
#         if not stock_record:
#     # If there's no stock record, continue to the next product
#           continue
#
#         current_stock_qty = stock_record['total_qty']
#         min_stock_threshold = product.get('min', 10)  # Fetch from product or default to 10
#
#         # Check if current stock is below the threshold
#         if current_stock_qty < min_stock_threshold:
#             print(product)
#             print(min_stock_threshold)
#             send_notification(product, current_stock_qty, min_stock_threshold)
#         else:
#             print("stock are found")
# time.sleep(6000)


# def send_notification(product, current_stock_qty, min_stock_threshold):
#     subject = f"Low Stock Alert: {product['product_name']} (SKU: {product['sku']})"
#     body = f"""
#     Alert! The stock of {product['product_name']} (SKU: {product['sku']}) has dropped below the minimum threshold of {min_stock_threshold} units.
#
#     Current Stock: {current_stock_qty}
#     Minimum Stock Threshold: {min_stock_threshold}
#
#     Please replenish the stock immediately.
#
#     Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#     """
#     try:
#         with app.app_context():
#             if send_email(subject, "shubhamlathiya2004@gmail.com", body):
#                 print(f"Low stock notification sent for {product['min']} (SKU: {product['sku']})")
#                 return jsonify({"message": "Personnel added and email sent!"}), 200
#             else:
#                 return jsonify({"error": "Failed to send email."}), 500
#     except Exception as e:
#         print(f"Failed to send email: {str(e)}")
#
#
# scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
# scheduler.add_job(monitor_stock_levels, 'cron', minute='*/3')
# scheduler.start()


if __name__ == '__main__':
    # try:
    app.run(debug=True)
# except (KeyboardInterrupt, SystemExit):
# Shutdown the scheduler gracefully
# scheduler.shutdown()
# print("Scheduler shutdown.")
