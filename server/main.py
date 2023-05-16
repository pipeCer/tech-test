import importlib
import os

from flasgger import Swagger
from flask import Flask
from flask_cors import CORS


def import_blueprints(flask_app):
    routes_path = os.listdir(
        os.path.dirname(
            os.path.abspath(__file__),
        ).replace('\\', '/') + '/routes',
    )
    for file in routes_path:
        if file.endswith('route.py'):
            module_name = file[:-3]
            module = importlib.import_module('routes.' + module_name)
            flask_app.register_blueprint(module.blueprint)


app = Flask(__name__)
CORS(app)
Swagger(app)
import_blueprints(app)
