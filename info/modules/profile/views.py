from flask import render_template, g
from . import profile_bp
from info.utils.common import get_user_data


@profile_bp.route("/info")
@get_user_data
def user_info():
    """
    个人中心
    :return:
    """
    user = g.user
    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template("profile/user.html", data=data)
