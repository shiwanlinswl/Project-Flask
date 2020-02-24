from info import constants
from info.models import User, News, Category
from info.response_code import RET
from info.utils.common import get_user_data
from . import index_bp
from flask import render_template, current_app, g
from flask import jsonify, request
from flask import session


@index_bp.route('/news_list')
def news_list():
    """
    新闻列表展示
    :return:
    """
    # 1.获取参数
    args_dict = request.args
    cid = args_dict.get("cid")
    p = args_dict.get("page", 1)
    per_page = args_dict.get("per_page", 10)

    # 2.校验参数
    if not cid:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 分页参数强转换为整型
    try:
        p = int(p)
        per_page = int(per_page)
        cid = int(cid)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")

    # 3.逻辑处理
    # News.status == 0 表示评审通过，才在新闻列表中展示
    filter_list = [News.status == 0]
    if cid != 1:
        # 添加查询条件到列表，使用时解包即可（可添加多个）
        filter_list.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(p, per_page, False)
        items = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻分页查询异常")

    news_list = []
    for news in items if items else []:
        news_list.append(news.to_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_list,
        "per_page": per_page
    }

    return jsonify(errno=RET.OK, errmsg="查询新闻列表成功", data=data)


@index_bp.route('/')
@get_user_data
def index():
    """
    新闻首页展示
    :return:
    """
    # -----1.用户登录后，显示用户信息-----

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

    # -----3.新闻分类显示-----
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻分类查询异常")

    category_dict_list = []
    for category in categories if categories else []:
        category_dict_list.append(category.to_dict())

    data = {
        "user_info": user_dict,
        "click_news_list": news_dict_list,
        "categories": category_dict_list
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
