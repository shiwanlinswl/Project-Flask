from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix="/admin")

from .views import *


# 使用请求钩子，对每次请求做处理
@admin_bp.before_request
def is_admin_user():
    """
    管理员用户权限管理
    """
    # 防止管理员用户无法登录, 对请求的url排除
    if request.url.endswith("admin/login"):
        # 走管理员登录逻辑
        pass
    else:
        user_id = session.get("user_id")
        is_admin = session.get("is_admin", False)
        if not user_id or not is_admin:
            # 如果用户未登录或不是管理员用户，则重定向到新闻首页/
            return redirect("/")