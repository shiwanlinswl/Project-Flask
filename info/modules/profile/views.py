from flask import render_template, g, request, jsonify, session, current_app

from info import db
from info.response_code import RET
from . import profile_bp
from info.utils.common import get_user_data


@profile_bp.route("/base_info", methods=["POST", "GET"])
@get_user_data
def user_base_info():
    """
    基本资料
    :return:
    """
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("profile/user_base_info.html", data=data)

    # 1.获取基本信息参数：signature，nick_name，gender；并校验
    json_dict = request.json
    signature = json_dict.get("signature")
    nick_name = json_dict.get("nick_name")
    gender = json_dict.get("gender")

    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="参数类型错误")

    # 3.修改用户对象属性
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    # 3.更新session中的昵称信息
    session["nick_name"] = nick_name

    # 4.保存修改后的信息到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="保存用户信息到数据库异常")

    return jsonify(errno=RET.OK, errmsg="OK")


@profile_bp.route("/info")
@get_user_data
def user_info():
    """
    个人中心
    :return:
    """
    user = g.user
    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template("profile/user.html", data=data)
