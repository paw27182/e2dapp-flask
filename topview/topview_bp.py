from pathlib import Path

from flask import Blueprint, current_app, render_template
from flask_login import current_user, login_required

mid = Path(__file__).name

topview_bp = Blueprint('topview_bp', __name__,
                       template_folder='templates/topview',
                       static_url_path='/topview/static',
                       static_folder='../topview/static',
                       )


@topview_bp.route("/topview")
@login_required
def topview():
    headline = current_app.config["APPLICATION_TITLE"]

    return render_template("topview.html",
                           headline=headline,
                           message="Login ID: " + current_user.username)
