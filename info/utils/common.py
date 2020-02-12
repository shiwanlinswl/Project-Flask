from flask import session, current_app, jsonify, g
from info.response_code import RET


# 自定义过滤器方法
def do_filter_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


# 自定义获取用户数据装饰器
def get_user_data(view_func):
    def wrapper(*args, **kwargs):
        # 从session中获取用户id
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger(e)
                return jsonify(errno=RET.DBERR, errmsg="数据库查询操作异常")
        # 使用g对象临时存储user对象
        g.user = user
        return view_func(*args, **kwargs)

    return wrapper
