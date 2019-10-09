from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from config import config_dict
import logging
from logging.handlers import RotatingFileHandler
from flask_session import Session

db = SQLAlchemy()

# # type:StrictRedis 提前声明redis_store数据类型
redis_store = None  # type:StrictRedis


def write_log(config_class):
    """
    记录日志方法
    :param config_class: 日志级别
    :return:
    """
    logging.basicConfig(level=config_class.LOG_LEVEL)  # 调试DEBUG级

    # 创建日志记录器，指明日志的路径，文件最大大小，文件上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=1)

    # 设置日志等级
    formatter = logging.Formatter('%(levelname)s %(filename)s: %(lineno)d %(message)s')

    # 为日志器设置日志格式
    file_log_handler.setFormatter(formatter)

    # 为全局日志对象添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """
    创建app方法
    :param config_name: 日志名称
    :return:
    """

    app = Flask(__name__)
    config_class = config_dict[config_name]
    app.config.from_object(config_class)

    write_log(config_class)

    # 2.创建mysql数据库对象
    # 当app有值时才整正的初始化操作  懒加载思想
    db.init_app(app)

    # 3.创建redis数据库对象
    global redis_store
    redis_store = StrictRedis(host=config_class.REDIS_HOST,
                              port=config_class.REDIS_PORT,
                              decode_responses=True
                              )

    # 4.开启后端的CSRF保护机制
    # 底层实现：
    # 1.提取cookie中的csrf_token的值
    # 2.提取表单中的csrf_token的值,或ajax请求中的X-CSRFToken的值
    # 3.对比这两个值是否相等，相等则校验通过
    CSRFProtect(app)

    # 5.借助Session调整flask.session的存储位置到redis中存储
    Session(app)

    return app
