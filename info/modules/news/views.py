from info import constants, db
from info.models import User, News, Comment, CommentLike
from info.response_code import RET
from info.utils.common import get_user_data
from . import news_bp
from flask import render_template, current_app, session, jsonify, g, abort, request


@news_bp.route('/comment_like', methods=["POST"])
@get_user_data
def comment_like():
    """
    评论点赞&取消点赞
    :return:
    """
    """
        1.获取参数：user, comment_id, action行为：点赞(add)/取消点赞(remove)
        2.参数校验
        3.逻辑处理
            3.1.根据comment_id查询新闻对象
            3.2.点赞：创建comment_like对象，并为属性赋值，保存到数据库
                ---对评论对象的comment_count + 1 
            3.3.取消点赞：移除comment_like对象，保存到数据库
                ---对评论对象的comment_count - 1 
        4.返回数据
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    json_dict = request.json
    comment_id = json_dict.get("comment_id")
    action = json_dict.get("action")

    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.DATAERR, errmsg="参数类型错误")

    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻对象异常")

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 根据行为参数判断点赞/取消点赞
    if action == "add":
        # 先查询评论点赞对象是否存在
        try:
            comment_like_obj = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                        CommentLike.user_id == user.id).first()
        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=RET.DBERR, errmsg="查询评论点赞异常")

        # 不存在才可以点赞
        if not comment_like_obj:
            comment_like = CommentLike()
            comment_like.comment_id = comment.id
            comment_like.user_id = user.id
            comment.like_count += 1
            db.session.add(comment_like)
    else:
        try:
            comment_like_obj = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                        CommentLike.user_id == user.id).first()
        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=RET.DBERR, errmsg="查询评论点赞异常")
        if comment_like_obj:
            db.session.delete(comment_like_obj)
            comment.like_count -= 1

    # 统一提交数据库操作
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="点赞/取消点赞提交数据库失败")
    return jsonify(errno=RET.OK, errmsg="OK")


@news_bp.route('/news_comment', methods=["POST"])
@get_user_data
def news_comment():
    """
    新闻评论--主&子评论
    :return:
    """
    """
    1.获取参数：user, news_id, content, parent_id
    2.参数校验
    3.逻辑处理
        3.1 查询新闻对象
        3.2 创建评论评论对象并对属性赋值
        3.3 保存数据到数据库
    4.返回数据
    """

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    json_dict = request.json
    parent_id = json_dict.get("parent_id")
    content = json_dict.get("comment")
    news_id = json_dict.get("news_id")

    if not all([content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻对象异常")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # 创建评论对象
    comment = Comment()
    comment.news_id = news.id
    comment.content = content
    comment.user_id = user.id

    # parent_id作为判断子评论和主评论的判断依据
    if parent_id:
        # 有parent_id:表示是子评论
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="评论保存失败")

    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


@news_bp.route('/news_collect', methods=["POST"])
@get_user_data
def news_collect():
    """
    新闻收藏&取消收藏
    :return:
    """
    # 1.获取参数news_id,action(值为collect,cancel_collect)
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    json_dict = request.json
    news_id = json_dict.get("news_id")
    action = json_dict.get("action")

    # 2.参数校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

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

    # -----5.查询评论列表-----
    try:
        comment_list = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻列表异常")

    # -----6.查询评论点赞-----
    # 定义全局变量：防止出现用户未登录报错
    comment_like_list = []
    # 用户登录后才显示
    if user:
        # 获取当前新闻的评论id列表
        comments = [comment.id for comment in comment_list]
        try:
            # 过滤出当前用户点过赞的新闻id
            comment_like_id_obj_list = CommentLike.query.filter(CommentLike.comment_id.in_(comments),
                                                                CommentLike.user_id == user.id).all()
        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=RET.DBERR, errmsg="查询评论点赞异常")

        # 获取当前用户点多赞的新闻id列表
        comment_like_list = [comment_like_id_obj.comment_id for comment_like_id_obj in comment_like_id_obj_list]

    comment_dict_list = []
    # 新闻列表对象转字典
    for comment in comment_list if comment_list else []:
        comment_dict = comment.to_dict()

        # 使用is_like属性标识是否点赞
        comment_dict["is_like"] = False
        if comment.id in comment_like_list:
            comment_dict["is_like"] = True

        comment_dict_list.append(comment_dict)

    data = {
        "user_info": user_dict,
        "click_news_list": news_dict_list,
        "news": news_dict,
        "is_collected": is_collected,
        "comments": comment_dict_list
    }

    return render_template("news/detail.html", data=data)
