from info import constants
from info.models import User, News
from info.response_code import RET
from . import index_bp
from flask import render_template, current_app
from flask import jsonify
from flask import session


@index_bp.route('/')
def index():
    # -----1.用户登录后，显示用户信息-----

    # 从session中获取用户id
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询操作异常")
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

    # print(news_dict_list)
    data = {
        "user_info": user_dict,
        "click_news_list": news_dict_list
    }

    return render_template("news/index.html", data=data)


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
