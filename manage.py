from flask import Flask, session
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager


class Config(object):
    """
    自定义配置类:罗列项目的配置
    """
    DEBUG = True

    # mysql连接配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@93.179.119.153:3306/info"
    # 开启数据库跟踪模式
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis连接配置
    REDIS_HOST = '93.179.119.153'
    REDIS_PORT = 6379

    # 配置密钥
    SECRET_KEY = 'AGASDGADS214GAGQHKHGJHRE5634GNMWTY1G'

    # 将flask中的session存储到redis数据库中
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


# 1.创建app对象
app = Flask(__name__)
app.config.from_object(Config)

# 2.创建mysql数据库对象
db = SQLAlchemy(app)

# 3.创建redis数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 4.开启后端的CSRF保护机制
# 底层实现：
# 1.提取cookie中的csrf_token的值
# 2.提取表单中的csrf_token的值,或ajax请求中的X-CSRFToken的值
# 3.对比这两个值是否相等，相等则校验通过
CSRFProtect(app)

# 5.借助session调整flask.session的存储位置
Session(app)

# 6.创建数据库管理对象,将app交给管理对象管理
manage = Manager(app)

# 7.数据库迁移初始化
Migrate(app, db)

# 8.添加迁移命令
manage.add_command("db", MigrateCommand)


@app.route('/')
def index():
    return 'Hello World'


if __name__ == '__main__':
    # 9.使用manage对象启动flask项目
    manage.run()
