from info import constants
from . import news_bp
from flask import render_template, current_app


@news_bp.route('/<int:news_id>')
def news_detail(news_id):
    """
    新闻详情展示
    :return:
    """
    return render_template("news/detail.html")


