from flask import render_template
from . import profile_bp


@profile_bp.route("/info")
def user_info():
    """
    个人中心
    :return:
    """
    data = {}
    return render_template("profile/user.html", data=data)
