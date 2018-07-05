#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'LittlePanic'

from flask_cors import CORS
from flask import Flask
from flask import render_template

# import os
# from flask_sqlalchemy import SQLAlchemy
# import pymysql

app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app, resources={"/api/*": {"origins": "*"}})
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:xiaofang123456@127.0.0.1:3306/wxapi"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app.config['SECRET_KEY'] = "xiaofang"
# app.debug = True  # try debug

from backend.app.admin import admin as admin_blueprint
from backend.app.home import home as home_blueprint

# app.register_blueprint(admin_blueprint,url_prefix = "/admin")
app.register_blueprint(admin_blueprint)
app.register_blueprint(home_blueprint)


@app.errorhandler(404)
def page_not_find(error):
    return render_template('404.html'), 404
