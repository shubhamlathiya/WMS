from flask import Flask, request, jsonify, render_template, Blueprint
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required
from config import mongo

admin = Blueprint('admin', __name__)


@admin.route('/dashboard', methods=['GET'])
@token_required
@role_required('admin_dashboard', 'view')
def dashboard_home(current_user):
#     result = list(mongo.db.page_visibility.find({
#     'roles.admin.permissions.view': 1,
#     'roles.admin.permissions.create': 1,
#     'roles.admin.permissions.edit': 1,
#     'roles.admin.permissions.delete': 1
# }, {
#     'roles.admin.permissions': 1,
#       'page_name': 1  # Only returns the admin permissions field
# }))
    # print(result)
    return render_template('dashboard/admin_dashboard.html')
