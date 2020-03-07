from flask_migrate import Migrate, MigrateCommand
from info import create_app, db
from flask_script import Manager
# from info.models import User


# 创建app对象
from info.models import User

app = create_app("development")

# 创建数据库管理对象,将app交给管理对象管理
manage = Manager(app)

# 数据库迁移初始化
Migrate(app, db)

# 添加迁移命令
manage.add_command("db", MigrateCommand)


"""
使用:python manage.py createsuperuser -n admin -p 123456
"""
@manage.option('-n', '--name', dest='name')
@manage.option('-p', '--password', dest='password')
def createsuperuser(name, password):
    """
    创建管理员用户
    :param name: 账号
    :param password: 密码
    :return:
    """
    if not all([name, password]):
        print("参数不足")
        return

    admin_user = User()
    admin_user.mobile = name
    admin_user.password = password
    admin_user.nick_name = name
    admin_user.is_admin = True

    # 保存到数据库
    try:
        db.session.add(admin_user)
        db.session.commit()
        print("创建管理员用户成功")
    except Exception as e:
        print(e)
        db.session.rollback()


if __name__ == '__main__':
    # 使用manage对象启动flask项目
    # print(app.url_map)
    manage.run()
