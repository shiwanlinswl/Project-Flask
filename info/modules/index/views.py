from . import index_bp
from flask import jsonify


@index_bp.route('/')
def index():
    return jsonify(msg="Hello World")
