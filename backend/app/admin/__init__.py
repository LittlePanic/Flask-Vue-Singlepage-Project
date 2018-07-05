# coding:utf8
from flask import Blueprint

admin = Blueprint("admin", __name__)

import backend.app.admin.views  # import views.py files
