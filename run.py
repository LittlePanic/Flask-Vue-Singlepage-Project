from flask import Flask, render_template, jsonify
from random import *
from flask_cors import CORS
import requests

app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/random')
def random_number():
    response = {
        'randomNumber': randint(1, 100)
    }
    return jsonify(response)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")

if __name__ == "__main__":
    # app.run(host='0.0.0.0',threaded=True, debug=True, port=5000, ssl_context=(
    #     "/home/nginx/ssl/214697773120607.pem",
    #     "/home/nginx/ssl/214697773120607.key")
    #     )
    app.run(debug=True)