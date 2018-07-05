# coding:utf8
from flask import Blueprint

home = Blueprint("home", __name__)

import backend.app.home.views  # import views.py files
