from flask import Flask, request, jsonify, render_template, Blueprint
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

client = Blueprint('client', __name__)


@client.route('/dashboard',endpoint='dashboard')
@token_required
def dashboard_client_home(current_user):
    return render_template('client/order_products.html')