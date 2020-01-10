from . import index_bp
from flask import render_template, current_app
from flask import jsonify


@index_bp.route('/')
def index():
    return render_template("news/index.html")


@index_bp.route('/favicon.ico')
def get_favicon():
    """
    get web favicon

    source code:
        Function used internally to send static files from the static
        folder to the browser.
    :return:
    """
    return current_app.send_static_file('news/favicon.ico')
