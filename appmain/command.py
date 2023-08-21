from datetime import datetime as dt
from pathlib import Path

import pandas as pd
from flask import current_app
from flask_login import current_user

from models.models import DatabaseInfo, FormInfo, FormList, GroupInfo, UserInfo, db

mid = Path(__file__).name
ftime = "%Y-%m-%d %H:%M:%S"


def create_db_instance(selected_form, /, key=None, key_type=None, primary_key=None):
    # get dbname
    obj = FormInfo.query.filter_by(formname=selected_form).first()
    group = obj.groupname
    obj = GroupInfo.query.filter_by(groupname=group).first()
    dbname = obj.dbname

    # get hostname, accessid and accesspwd
    obj = DatabaseInfo.query.filter_by(dbname=dbname).first()
    hostname = obj.hostname
    accessid = obj.accessid
    accesspwd = obj.accesspwd

    # set tablename
    tablename = selected_form

    database_type = current_app.config["DATABASE_TYPE"]

    if "SQLite3" in database_type:
        from appmain.dbaccess import DBAccess
        db_f = DBAccess(dbname, tablename, key, key_type, primary_key)
    elif "MongoDB" in database_type:
        from appmain.dbaccessmongodb import DBAccess
        db_f = DBAccess(dbname, tablename, hostname, accessid, accesspwd, key, key_type, primary_key)
    elif "PostgreSQL" in database_type:
        from appmain.dbaccesspostgresql import DBAccess
        db_f = DBAccess(dbname, tablename, hostname, accessid, accesspwd, key, key_type, primary_key)
    else:
        db_f = None
    return db_f, group


def database_info_entry(input_data):
    print(f"[{mid}] database_info_entry")

    # check privilege
    db_administrator = current_app.config["DB_ADMINISTRATOR"]
    if current_user.username not in db_administrator:
        return "NG", "privilege error"  # alert

    # clear table
    for obj in DatabaseInfo.query.filter_by().all():
        db.session.delete(obj)
        db.session.commit()

    # make a new entry or update the existing
    for item in input_data:
        target_dbname = item[0]
        obj = DatabaseInfo.query.filter_by(dbname=target_dbname).first()
        if not obj:
            obj = DatabaseInfo(dbname=item[0],
                               hostname=item[1],
                               accessid=item[2],
                               accesspwd=item[3],
                               administrator1=item[4],
                               administrator2=item[5],
                               modified_by=current_user.username)
        else:
            obj.hostname = item[1]
            obj.accessid = item[2]
            obj.accesspwd = item[3]
            obj.administrator1 = item[4]
            obj.administrator2 = item[5]
            obj.modified_by = current_user.username

        db.session.add(obj)
        db.session.commit()

    return "OK", "Done."  # alert


def group_info_entry(input_data):
    print(f"[{mid}] group_info_entry")

    # in case user is DB_ADMINISTRATOR
    if current_user.username in current_app.config["DB_ADMINISTRATOR"]:
        # replace group records
        for obj in GroupInfo.query.filter_by().all():
            if obj.rolename in ["GROUP_ADMINISTRATOR"]:
                db.session.delete(obj)
                db.session.commit()

        for item in input_data:
            obj = GroupInfo(groupname=item[0],
                            dbname=item[1],
                            username=item[2],
                            rolename="GROUP_ADMINISTRATOR",
                            modified_by=current_user.username)
            db.session.add(obj)
            db.session.commit()

        return "OK", "Done."  # alert

    # in case user is GROUP_ADMINISTRATOR
    for user in GroupInfo.query.filter_by(username=current_user.username).all():
        if user.rolename in ["GROUP_ADMINISTRATOR"]:
            # delete GROUP_USER
            group_administrator_list = list()
            for obj in GroupInfo.query.filter_by(groupname=user.groupname).all():
                if obj.rolename not in ["GROUP_ADMINISTRATOR"]:  # GROUP_USER
                    db.session.delete(obj)
                    db.session.commit()

                else:
                    group_administrator_list.append(obj.username)

            # add GROUP_USER
            for item in input_data:
                if item[2] not in group_administrator_list:
                    obj = GroupInfo(groupname=item[0],
                                    dbname=item[1],
                                    username=item[2],
                                    rolename="GROUP_USER",
                                    modified_by=current_user.username)
                    db.session.add(obj)
                    db.session.commit()
                else:
                    pass
        else:
            pass

    return "OK", "Done."  # alert


def form_info_entry(input_data):
    print(f"[{mid}] form_info_entry")

    # check privilege
    for group in pd.DataFrame(input_data, columns=["formname", "groupname"]) \
            .loc[:, "groupname"]\
            .unique():
        group_administrator_list = list()
        for obj in GroupInfo.query.filter_by(groupname=group).all():
            if obj.rolename in ["GROUP_ADMINISTRATOR"]:
                group_administrator_list.append(obj.username)

        if current_user.username in group_administrator_list:
            continue
        else:
            return "NG", "privilege error"  # alert

    # clear FormInfo
    for group in pd.DataFrame(input_data, columns=["formname", "groupname"]) \
            .loc[:, "groupname"]\
            .unique():
        for obj in FormInfo.query.filter_by(groupname=group).all():
            db.session.delete(obj)
            db.session.commit()

    # add FormInfo
    alert = "OK", "Done."
    for item in input_data:
        obj = FormInfo.query.filter_by(formname=item[0]).first()
        if obj:
            alert = ('NG', f'error: the same name "{item[0]}" already exists on the other group.  please change the name')
            break
        else:
            obj = FormInfo(formname=item[0],
                           groupname=item[1],
                           modified_by=current_user.username)
            db.session.add(obj)
            db.session.commit()

    return alert


def write_form_items(input_data, control_data_dict):
    print(f"[{mid}] write_form_items")

    # extract data out of control_data_dict
    selected_form = control_data_dict["file_name"]
    key = control_data_dict["key"]
    key_type = control_data_dict["key_type"]
    primary_key = control_data_dict["primary_key"]

    # check selected_form exists on FormInfo
    obj = FormInfo.query.filter_by(formname=selected_form).first()
    if not obj:
        return "NG", "error: form_entry doesn't exist.  please entry form information previously."  # alert

    # check privilege
    obj = FormInfo.query.filter_by(formname=selected_form).first()
    group = obj.groupname
    group_user_list = list()
    for obj in GroupInfo.query.filter_by(groupname=group).all():
        group_user_list.append(obj.username)

    if current_user.username not in group_user_list:
        return "NG", "privilege error"  # alert

    # create instance object and write item(s)
    db_f, group = create_db_instance(selected_form, key, key_type, primary_key)
    alert = db_f.write_form_items(input_data)

    # add to the form list
    obj = FormList.query.filter_by(formname=selected_form).first()
    if obj:
        db.session.delete(obj)
        db.session.commit()

    obj = FormList(formname=selected_form,
                   form_size=db_f.get_form_size(selected_form),
                   groupname=group,
                   form_meta_data=" ".join(control_data_dict["key"]),
                   modified_by=current_user.username)
    db.session.add(obj)
    db.session.commit()

    return alert


def read_form_items(command, selected_form):
    print(f"[{mid}] {command= } {selected_form= }")

    # create instance object and read item(s)
    db_f, group = create_db_instance(selected_form)
    key, items = db_f.read_form_items(command)

    return key, items


def get_a_list_of_forms():
    print(f"[{mid}] get_a_list_of_forms")

    result = list()
    for user in GroupInfo.query.filter_by(username=current_user.username).all():
        for obj in FormList.query.filter_by(groupname=user.groupname).all():
            result.append([obj.formname, obj.form_size, obj.groupname, obj.update_at.strftime(ftime), obj.modified_by])

    result.sort(key=lambda x: x[0])
    items = [[i+1, *item] for i, item in enumerate(result)]
    return items


def get_a_list_of_forms_for_privilege():
    print(f"[{mid}] get_a_list_of_forms_for_privilege")

    groups = list()
    for user in GroupInfo.query.filter_by(username=current_user.username).all():
        # check privilege
        if user.rolename in ["GROUP_ADMINISTRATOR"]:
            groups.append(user.groupname)

    # check privilege
    if current_user.username in current_app.config["DB_ADMINISTRATOR"]:
        for obj in GroupInfo.query.filter_by().all():
            groups.append(obj.groupname)
        groups = set(groups)

    items = list()

    # group_info_entry
    count = 0
    for group in groups:
        count += GroupInfo.query.filter_by(groupname=group).count()

    items.append([1, "group_info_entry",
                  count,
                  "-",
                  dt.now().strftime(ftime),
                  current_user.username])

    # form_info_entry
    count = 0
    for group in groups:
        count += FormInfo.query.filter_by(groupname=group).count()

    items.append([2, "form_info_entry",
                  count,
                  "-",
                  dt.now().strftime(ftime),
                  current_user.username])

    return items


def read_form_items_for_privilege(command, selected_form):
    print(f"[{mid}] {command= } {selected_form= }")

    groups = list()
    for user in GroupInfo.query.filter_by(username=current_user.username).all():
        # check privilege
        if user.rolename in ["GROUP_ADMINISTRATOR"]:
            groups.append(user.groupname)

    # check privilege
    if current_user.username in current_app.config["DB_ADMINISTRATOR"]:
        for obj in GroupInfo.query.filter_by().all():
            groups.append(obj.groupname)
        groups = set(groups)

    # group_info_entry
    if selected_form in ["group_info_entry"]:
        key = ["formname", "groupname", "dbname", "username", "rolename", "update_at", "modified_by"]
        items = list()
        for group in groups:
            for obj in GroupInfo.query.filter_by(groupname=group).all():
                items.append(["-", obj.groupname, obj.dbname, obj.username, obj.rolename, obj.update_at.strftime(ftime), obj.modified_by])

    # form_info_entry
    elif selected_form in ["form_info_entry"]:
        key = ["formname", "groupname", "dbname", "username", "rolename", "update_at", "modified_by"]
        items = list()
        for group in groups:
            for obj in FormInfo.query.filter_by(groupname=group).all():
                items.append([obj.formname, obj.groupname, "-", "-", "-", obj.update_at.strftime(ftime), obj.modified_by])
    else:
        key = []
        items = []

    items.sort(key=lambda x: x[0])  # sort according to the name
    return key, items


def get_a_list_of_signup_users():
    print(f"[{mid}] get_a_list_of_signup_users")

    # check privilege
    db_administrator = current_app.config["DB_ADMINISTRATOR"]
    if current_user.username not in db_administrator:
        return [[1, "signup_users", 0, "-", dt.now().strftime(ftime), current_user.username]]

    # count users
    count = UserInfo.query.filter_by().count()

    items = list()

    items.append([1, "signup_users",
                  count,
                  "-",
                  dt.now().strftime(ftime),
                  current_user.username])

    return items


def read_signup_users():
    key = ["formname", "groupname", "dbname", "username", "update_at", "modified_by"]

    items = list()

    # check privilege
    db_administrator = current_app.config["DB_ADMINISTRATOR"]
    if current_user.username not in db_administrator:
        return key, items

    for obj in UserInfo.query.filter_by().all():
        items.append(["-", "-", "-", obj.username, obj.update_at.strftime(ftime), obj.modified_by])

    return key, items


def drop_form(selected_form):
    print(f"[{mid}] drop_item {selected_form= }")

    # create instance object
    db_f, group = create_db_instance(selected_form)

    try:
        db_f.drop_form()

        # delete form out of FormList
        obj = FormList.query.filter_by(formname=selected_form).first()
        if obj:
            db.session.delete(obj)
            db.session.commit()
        return "OK", "Done."  # alert
    except Exception as err:
        return "NG", f"error: {err}"  # alert


def delete_item(selected_form, record_to_be_processed):
    print(f"[{mid}] delete_item {selected_form= } {record_to_be_processed= }")

    # create instance object and delete item
    db_f, group = create_db_instance(selected_form)
    db_f.delete_item(record_to_be_processed)

    # update the form list
    obj = FormList.query.filter_by(formname=selected_form).first()
    obj.form_size = db_f.get_form_size(selected_form)
    obj.modified_by = current_user.username

    db.session.add(obj)
    db.session.commit()


def delete_user(selected_form, record_to_be_processed):
    print(f"[{mid}] delete_item {selected_form= } {record_to_be_processed= }")

    user_to_be_deleted = record_to_be_processed.split(",")[4][2:-1]

    try:
        # delete user out of UserInfo
        obj = UserInfo.query.filter_by(username=user_to_be_deleted).first()
        if obj:
            db.session.delete(obj)
            db.session.commit()
        return "OK", "Done."  # alert
    except Exception as err:
        return "NG", f"error: {err}"  # alert


def checkup_resources():
    pass
    # TODO
    # formlistからDBに実体のないものを削除する
