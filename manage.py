from flask_migrate import Migrate, MigrateCommand
from info import create_app, db
from flask_script import Manager
# from info.models import User


# 创建app对象
app = create_app("development")

# 创建数据库管理对象,将app交给管理对象管理
manage = Manager(app)

# 数据库迁移初始化
Migrate(app, db)

# 添加迁移命令
manage.add_command("db", MigrateCommand)

if __name__ == '__main__':
    # 使用manage对象启动flask项目
    # print(app.url_map)
    manage.run()
