import json
import re
from pathlib import Path

import numpy as np
from flask import (Blueprint, current_app, redirect, render_template, request,
                   session)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.security import check_password_hash, generate_password_hash

from models.models import UserInfo, db

mid = Path(__file__).name
ftime = "%Y/%m/%d %H:%M:%S"

auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates/auth',
                    static_url_path='/auth/static',
                    static_folder='../auth/static',
                    )

login_manager = LoginManager()
login_manager.init_app(current_app)  # for login_user()


@auth_bp.route("/", methods=["GET"])
def index():
    return redirect("/login")  # slash


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # login_manager.init_app(current_app)  # for login_user()

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # print(f"{username= } {password= }")
        user = UserInfo.query.filter_by(
            username=username).first()  # search User table
        if not user:
            return json.dumps({"status": "NG", "message": "login failed."})

        if check_password_hash(user.password, password):
            login_user(user)

            # session object is not used.
            session["user"] = current_user.username

            msg = f'++++++ login +++ {current_user.username}'
            current_app.logger.info(msg)
            return redirect("/topview")  # slash

        else:
            return json.dumps({"status": "NG", "message": "login failed."})
    else:
        headline = current_app.config["APPLICATION_TITLE"]
        jumbotron_image = str(np.random.randint(1, 6, 1)[0]) + ".jpg"  # [1,5]
        return render_template("login.html",
                               headline=headline,
                               jumbotron_image=jumbotron_image,
                               )


# Signup
@auth_bp.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        return json.dumps({"status": "sorry, UNDISCLOSED"})
    else:
        return render_template('signup.html')


# Change password
@auth_bp.route("/changepassword", methods=['GET', 'POST'])
def changepassword():
    if request.method == "POST":
        return json.dumps({"status": "sorry, UNDISCLOSED"})
    else:
        return render_template('changepassword.html')


@auth_bp.route('/logout', methods=["GET"])
@login_required
def logout():
    msg = f'+++++ logout +++ {current_user.username}'
    current_app.logger.info(msg)

    session.pop("user", None)  # session object is not used.

    logout_user()
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))
