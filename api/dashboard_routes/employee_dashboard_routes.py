from flask import Flask, request, jsonify, render_template, Blueprint
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

employee = Blueprint('employee', __name__)


@employee.route('/dashboard', methods=['GET'])
@token_required
@role_required('employee_dashboard', 'view')
def dashboard_home(current_user):
    print("hy")
    return render_template('dashboard/employee_dashboard.html')
