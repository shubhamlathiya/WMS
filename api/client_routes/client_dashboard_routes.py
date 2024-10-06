from flask import Flask, request, jsonify, render_template, Blueprint
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required
from . import client



@client.route('/dashboard', methods=['GET'], endpoint='dashboard')
@token_required
@role_required('client_dashboard', 'view')
def dashboard_home(current_user):
    return render_template('client/client_dashboard.html')
