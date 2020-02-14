from info import constants, db
from info.models import User, News
from info.response_code import RET
from info.utils.common import get_user_data
from . import news_bp
from flask import render_template, current_app, session, jsonify, g, abort, request


@news_bp.route('/news_collect', methods=["POST"])
@get_user_data
def news_collect():
    """
    新闻收藏&取消收藏
    :return:
    """
    # 1.获取参数news_id,action(值为collect,cancel_collect)
    json_dict = request.json
    news_id = json_dict.get("news_id")
    action = json_dict.get("action")
    user = g.user

    # 2.参数校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 3.处理业务逻辑
    # 3.1 判断action参数
    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")

    # 3.2 获取新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DATAERR, errmsg="查询新闻数据异常")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    if action:
        # 3.3 收藏：将当前新闻对象添加到用户新闻收藏列表中
        if action == "collect":
            user.collection_news.append(news)
        # 3.4 取消收藏：将当前新闻对象从用户新闻收藏列表中移除
        else:
            if news in user.collection_news:
                user.collection_news.remove(news)

        # 3.5提交修改结果到数据库
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger(e)
            db.session.rollback()
            return jsonify(errno=RET.DATAERR, errmsg="修改是否收藏异常")

    # 4.返回数据
    return jsonify(errno=RET.OK, errmsg="收藏成功")


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

    # -----3.获取新闻详情信息-----
    news_obj = None
    try:
        news_obj = News.query.get(news_id)
    except Exception as e:
        current_app.logger(e)
        abort(404)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻数据异常")

    # 新闻点击量累加(这里未做数据库提交操作)
    news_obj.clicks += 1

    news_dict = news_obj.to_dict() if news_obj else None

    # -----4.显示新闻是否收藏-----
    # 定义is_collected字段标识是否收藏，默认未收藏
    is_collected = False
    # 用户对象存在时，才显示收藏状态，否则都为未收藏
    if user:
        # 判断依据：当前新闻对象是否在用户对象的收藏列表中
        if news_obj in user.collection_news:
            is_collected = True

    data = {
        "user_info": user_dict,
        "click_news_list": news_dict_list,
        "news": news_dict,
        "is_collected": is_collected
    }

    return render_template("news/detail.html", data=data)
