"""
Database -- 1:N -- Group -- 1:N -- User
                     |
                    1:N
                     |
                   Form

"""
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# database information
class DatabaseInfo(db.Model):
    __tablename__ = "databaseinfo"
    id = db.Column(db.Integer, primary_key=True)
    dbname = db.Column(db.String(50), nullable=False, unique=True)
    hostname = db.Column(db.String(50), nullable=True)
    accessid = db.Column(db.String(50), nullable=True)
    accesspwd = db.Column(db.String(100), nullable=True)
    administrator1 = db.Column(db.String(50), nullable=False)
    administrator2 = db.Column(db.String(50), nullable=True)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    # update_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.String(50), nullable=False)


# group information
class GroupInfo(db.Model):
    __tablename__ = "groupinfo"
    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(50), nullable=False)
    dbname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    rolename = db.Column(db.String(50), nullable=False)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    modified_by = db.Column(db.String(50), nullable=False)


# form information
class FormInfo(db.Model):
    __tablename__ = "forminfo"
    id = db.Column(db.Integer, primary_key=True)
    formname = db.Column(db.String(50), nullable=False, unique=True)
    groupname = db.Column(db.String(50), nullable=False)
    # form_meta_data = db.Column(db.String(500), nullable=True)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    modified_by = db.Column(db.String(50), nullable=False)


# form list display
class FormList(db.Model):
    __tablename__ = "formlist"
    id = db.Column(db.Integer, primary_key=True)
    formname = db.Column(db.String(50), nullable=False, unique=True)
    form_size = db.Column(db.Integer, nullable=False, default=0)
    groupname = db.Column(db.String(50), nullable=False)
    form_meta_data = db.Column(db.String(500), nullable=True)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    modified_by = db.Column(db.String(50), nullable=False)


# user information
class UserInfo(UserMixin, db.Model):
    __tablename__ = "userinfo"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    modified_by = db.Column(db.String(50), nullable=False)
