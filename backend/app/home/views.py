from . import home
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from random import *
from backend.app import app
import requests


@home.route('/api/random')
def random_number():
    response = {
        'randomNumber': randint(1, 100)
    }
    return jsonify(response)


@home.route('/', defaults={'path': ''})
@home.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")
