import re
import random
from . import passport_bp
from flask import request, current_app, abort, make_response, jsonify
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants
from info.response_code import *
from info.models import User
from info.lib.yuntongxun.sms import CCP


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
