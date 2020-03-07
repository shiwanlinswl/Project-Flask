from flask import request, render_template, current_app, jsonify, session, redirect, url_for

from info.models import User
from info.response_code import RET
from . import admin_bp


@admin_bp.route("/")
def admin_index():
    """
    管理员首页
    :return:
    """
    return render_template("admin/index.html")


@admin_bp.route("/login", methods=["POST", "GET"])
def admin_login():
    """
    管理员登录
    :return:
    """
    if request.method == "GET":
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