from . import passport_bp
from flask import request, current_app, abort, make_response, jsonify
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants
from info.response_code import *


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
