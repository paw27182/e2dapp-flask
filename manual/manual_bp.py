from flask import Blueprint
from flask import redirect

manual_bp = Blueprint('manual_bp', __name__,
                      template_folder='templates/manual',
                      static_url_path='/manual/static',
                      static_folder='../manual/static',
                      )


@manual_bp.route("/manual", methods=["GET"])
def manual():
    return redirect("/manual/static/html/index.html")
