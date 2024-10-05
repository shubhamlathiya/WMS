from flask import Blueprint, render_template, request, jsonify, redirect

from config import mongo
from middleware.auth_middleware import token_required
from middleware.page_visibility_middleware import role_required

area = Blueprint('area', __name__)


@area.route('/viewarea', methods=['GET'], endpoint='view')
@token_required
@role_required('areas', 'view')
def area_home(current_user):
    area = list(mongo.db.areas.find())
    return render_template('area/../../templates/product/area.html', area=area)


@area.route('/addarea', methods=['POST'])
@token_required
@role_required('areas', 'create')
def add_area(current_user):
    try:
        print(current_user)
        name = request.form.get('areaName')
        no_box = request.form.get('boxNo')
        # print(name)
        # found = mongo.db.areas.find({'area_name': name})
        # if found:
        #     return jsonify({'message': 'area already exists'}), 400

        area_record = {
            "area_name": name,
            "no_box": int(no_box),
            "status": 'true'
        }

        # Insert the product into MongoDB
        mongo.db.areas.insert_one(area_record)
        return redirect('/area/viewarea')

    except Exception as e:
        return redirect('/area/viewarea')
