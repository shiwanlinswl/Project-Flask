import time
from datetime import datetime, timedelta
from flask import request, render_template, current_app, jsonify, session, redirect, url_for, g

from info.utils.common import get_user_data
from info.models import User
from info.response_code import RET
from . import admin_bp


@admin_bp.route('/user_count')
def user_count():
    """
    查询总人数
    :return:
    """
    # 查询总人数
    total_count = 0
    try:
        # 非管理员用户
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新增数
    mon_count = 0
    try:
        now = time.localtime()
        mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
        mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日新增数
    day_count = 0
    try:
        day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询图表信息
    # 获取到当天00:00:00时间

    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 定义空数组，保存数据
    active_date = []
    active_count = []

    # 依次添加数据，再反转
    for i in range(0, 31):
        begin_date = now_date - timedelta(days=i)
        end_date = now_date - timedelta(days=(i - 1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)

    active_date.reverse()
    active_count.reverse()

    data = {"total_count": total_count, "mon_count": mon_count, "day_count": day_count, "active_date": active_date,
            "active_count": active_count}

    return render_template('admin/user_count.html', data=data)


@admin_bp.route("/")
@get_user_data
def admin_index():
    """
    管理员首页
    :return:
    """
    # 获取登录的管理员用户对象
    admin_user = g.user

    data = {
        "user": admin_user.to_dict() if admin_user else None
    }
    return render_template("admin/index.html", data=data)


@admin_bp.route("/login", methods=["POST", "GET"])
def admin_login():
    """
    管理员登录
    :return:
    """
    if request.method == "GET":
        # 优化:访问admin/login 接口，如果用户已登录，直接重定向到admin/ 首页
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:
            return redirect(url_for("admin.admin_index"))
        else:
            return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不足")

    # 查询用户对象
    admin_user = None  # type:User
    try:
        admin_user = User.query.filter(User.is_admin == True, User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户异常")

    # 校验用户是否为管理员用户
    if not admin_user:
        return render_template("admin/login.html", errmsg="用户不存在")

    # 校验密码
    if not admin_user.check_password(password):
        return render_template("admin/login.html", errmsg="密码错误")

    # 登录用户,记录session信息
    session["user_id"] = admin_user.id
    session["nick_name"] = admin_user.nick_name
    session["mobile"] = admin_user.mobile
    session["is_admin"] = True

    return redirect(url_for("admin.admin_index"))
