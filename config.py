from flask_pymongo import PyMongo

mongo = PyMongo()

def init_app(app):
    app.config['MONGO_URI'] = 'mongodb+srv://priyankmangroliya1:dGpa9volBVnWtL4r@cluster0.owrwz.mongodb.net/WMS'
    mongo.init_app(app)
