from datetime import datetime
import re
import random
from . import passport_bp
from flask import request, current_app, abort, make_response, jsonify, session
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants
from info.response_code import *
from info.models import User
from info.lib.yuntongxun.sms import CCP
from info import db


@passport_bp.route("/login", methods=["POST"])
def login():
    """
    登录
    :return:
    """
    # 1.获取参数
    json_dict = request.json
    mobile = json_dict.get("mobile")
    password = json_dict.get("password")

    # 2.校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match("^1[3578][0-9]{9}$", mobile):
        return jsonify(errno=RET.UNKOWNERR, errmsg="手机格式不正确")

    # 3.逻辑处理
    try:
        query_user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询异常")

    if not query_user:
        return jsonify(errno=RET.DATAERR, errmsg="用户不存在")

    if not query_user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg="密码输入错误")

    # 记录用户状态
    session["user_id"] = query_user.id
    session["nick_name"] = query_user.nick_name
    session["mobile"] = query_user.mobile

    # 修改用户最后一次登录时间，并提交到数据库
    query_user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库提交异常")

    # 4.响应数据
    return jsonify(errno=RET.OK, errmsg="登录成功")


# get请求地址 url="/passport/image_code?code_id=UUID"
@passport_bp.route("/image_code")
def get_image_code():
    """
    获取图片验证码
    :return:
    """
    # 1. 获取请求参数:将获取的UUID作为key存储到redis数据库中
    code_id = request.args.get("code_id")
    # 2.校验参数:code_id非空检验
    if not code_id:
        current_app.logger.error("参数不足")
        abort(404)
    # 3.逻辑处理:生成图片验证码的真实值，将code_id作为key存储图片的真实值到redis数据库
    image_name, real_image_code, image_data = captcha.generate_captcha()

    try:
        redis_store.setex("CODE_{}".format(code_id), constants.IMAGE_CODE_REDIS_EXPIRES, real_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg="保存图片验证码失败"))

    # 4.返回:相应验证码图片,返回的数据是二进制格式，不一定能兼容所有的浏览器
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/JPEG"
    return response


@passport_bp.route("/sms_code", methods=["POST"])
def send_code():
    """
    发送短信验证码
    :return:
    """

    # 1.获取参数:mobile,image_code
    json_dict = request.json
    mobile = json_dict.get("mobile")
    image_code = json_dict.get("image_code")
    image_code_id = json_dict.get("image_code_id")

    # 2.校验参数:个数校验，手机格式校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match("^1[3578][0-9]{9}$", mobile):
        return jsonify(errno=RET.UNKOWNERR, errmsg="手机格式不正确")

    # 3.逻辑处理:短信验证码判断，手机号是否注册判断，生成短信验证码，保存验证码到redis，发送短信验证码

    try:
        real_image_code = redis_store.get("CODE_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="获取真实图片验证码失败")

    if not real_image_code:
        current_app.logger.error("图片验证码已过期")
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")

    if image_code.lower() != real_image_code.lower():
        current_app.logger.error("验证码输入错误")
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    user = User.query.filter(User.mobile == mobile).first()
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已注册")

    sms_code = random.randint(0, 9999)
    # 不足6位前面补0
    sms_code = "%06d" % sms_code
    current_app.logger.info(sms_code)

    result = CCP().send_template_sms(mobile, [sms_code, 5], "1")

    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信验证码失败")

    try:
        redis_store.setex("sms_code_{}".format(mobile), constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存短信验证码失败")

    # 4.响应数据
    return jsonify(errno=RET.OK, errmsg="发送短信成功")


@passport_bp.route("/register", methods=["POST"])
def register():
    """
    注册
    :return:
    """
    # 1.获取校验:mobile,sms_code,password
    json_dict = request.json
    mobile = json_dict.get("mobile")
    sms_code = json_dict.get("smscode")
    password = json_dict.get("password")
    # 2.参数校验:数量校验，短信验证码正确性校验
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match("^1[3578][0-9]{9}$", mobile):
        return jsonify(errno=RET.UNKOWNERR, errmsg="手机格式不正确")

    try:
        real_sms_code = redis_store.get("sms_code_{}".format(mobile))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="查询短信验证码异常")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")

    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码输入有误")

    # 删除redis数据
    try:
        redis_store.delete("sms_code_{}".format(mobile))
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DATAERR, errmsg="删除短信验证码失败")

    # 3.逻辑处理
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = mobile
    # 记录最后一次登录时间
    user.last_login = datetime.now()

    # 密码加密处理,动态添加password属性
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 失败则回滚
        db.session.rollback()
        return jsonify(errno=RET.DATAERR, errmsg="数据库保存失败")

    # 注册成功，保存用户登录状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 4.返回数据
    return jsonify(errno=RET.OK, errmsg="注册成功")
