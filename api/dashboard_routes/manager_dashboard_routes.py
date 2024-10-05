from flask import Flask, request, jsonify, render_template, Blueprint
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

manager = Blueprint('manager', __name__)


@manager.route('/dashboard', methods=['GET'])
@token_required
@role_required('manager_dashboard', 'view')
def dashboard_home(current_user):
    return render_template('dashboard/manager_dashboard.html')
