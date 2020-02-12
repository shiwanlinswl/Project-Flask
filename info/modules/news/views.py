from info import constants
from info.models import User, News
from info.response_code import RET
from info.utils.common import get_user_data
from . import news_bp
from flask import render_template, current_app, session, jsonify, g


@news_bp.route('/<int:news_id>')
@get_user_data
def news_detail(news_id):
    """
    新闻详情展示
    :return:
    """
    # 从g对象中获取用户对象
    user = g.user
    """
    if user:
        user_dict = user.to_dict()
    """
    user_dict = user.to_dict() if user else None

    # -----2.获取新闻点击排行-----
    try:
        new_rank_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻数据查询异常")

    news_dict_list = []
    for news in new_rank_list if new_rank_list else []:
        news_dict_list.append(news.to_dict())

    data = {
        "user_info": user_dict,
        "click_news_list": news_dict_list,
    }

    return render_template("news/detail.html", data=data)
