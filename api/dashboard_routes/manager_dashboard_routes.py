# from flask import Flask, request, jsonify, render_template, Blueprint
# from middleware.auth_middleware import token_required
# from middleware.page_visibility_middleware import role_required
#
# dashboard = Blueprint('dashboard', __name__)
#
# @dashboard.route('/', methods=['GET'])
# @token_required
# # @role_required('dashboard')
# def dashboard_home(current_user):
#     return render_template('dashboard/admin_dashboard.html')
