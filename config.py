from redis import StrictRedis
from info.utils.tasks import create_tasks
import logging


class Config(object):
    """
    自定义配置类:罗列项目的配置
    """
    DEBUG = True

    # mysql连接配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:xxxxxx@93.179.119.153:3306/info22"
    # 开启数据库跟踪模式
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    JOBS = [{
        'id': 'job1',
        'func': create_tasks,
        'args': '',
        'trigger': 'corn',
        'seconds': 15
    }]

    # redis连接配置
    REDIS_HOST = '93.179.119.153'
    REDIS_PORT = 6379

    # 配置密钥
    SECRET_KEY = 'AGASDGADS214GAGQHKHGJHRE5634GNMWTY1G'

    # 将flask中的session(默认是存储到flask内存中)存储到redis数据库中
    # 指定存储的数据库类型
    SESSION_TYPE = "redis"

    # 指定session数据的具体存放位置 db:表示第几号库
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=5)

    # session存储的数据后产生session_id需要加密
    SESSION_USE_SIGNER = True

    # 设置session时长(默认是永久)
    SESSION_PERMANENT = False
    # 设置session过期时长 默认值 单位:秒
    PERMANENT_SESSION_LIFETIME = 86400


class DevelopmentConfig(Config):
    """
    开发模式配置类
    """
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """
    生产模式配置类
    """
    DEBUG = False
    LOG_LEVEL = logging.ERROR


config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
