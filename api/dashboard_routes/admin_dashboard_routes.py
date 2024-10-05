from flask import Flask, request, jsonify, render_template, Blueprint
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

admin = Blueprint('dashboard', __name__)


@admin.route('/dashboard', methods=['GET'])
@token_required
@role_required('admin_dashboard', 'view')
def dashboard_home(current_user):
    return render_template('dashboard/admin_dashboard.html')
