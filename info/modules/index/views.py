from . import index_bp
from flask import jsonify
from flask import render_template



@index_bp.route('/')
def index():
    return render_template("news/index.html")
