from flask import Blueprint

# url_prefix: 路由前缀
passport_bp = Blueprint("passport", __name__, url_prefix="/passport")

from .views import *
