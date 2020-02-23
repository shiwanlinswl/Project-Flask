from flask import render_template, g, request, jsonify, session, current_app

from info import db
from info.response_code import RET
from . import profile_bp
from info.utils.common import get_user_data
from info.utils.pic_storage import pic_storage
from info import constants


@profile_bp.route("/pic_info", methods=["POST", "GET"])
@get_user_data
def pic_info():
    """
    用户头像
    :return:
    """
    if request.method == "GET":
        return render_template("profile/user_pic_info.html")

    # 获取文件参数
    avatar = request.files.get("avatar")
    avatar_data = avatar.read()

    user = g.user

    # 上传图片
    try:
        pic_name = pic_storage(avatar_data)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.PARAMERR, errmsg="图片上传到平台异常")

    if not pic_name:
        return jsonify(errno=RET.DATAERR, errmsg="图片数据为空")

    # 将图片保存到数据库
    user.avatar_url = pic_name

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片到数据库失败")

    # 返回图片完整url地址
    full_avatar_url = constants.QINIU_DOMIN_PREFIX + pic_name

    return jsonify(errno=RET.OK, errmsg="返回图片成功", data=full_avatar_url)


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
