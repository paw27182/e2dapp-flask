import io
import random
import zipfile
from datetime import datetime as dt
from pathlib import Path

from flask import (Blueprint, current_app, render_template, request,
                   send_from_directory)
from flask_login import current_user

import appmain.command as cmd
import appmain.utilities as utl
from models.models import FormInfo, FormList, GroupInfo

mid = Path(__file__).name
ftime = "%Y/%m/%d %H:%M:%S"

appmain_bp = Blueprint('appmain_bp', __name__,
                       template_folder='templates/appmain',
                       static_url_path='/appmain/static',
                       static_folder='../appmain/static',
                       )


def prepare_working_dir(user):
    working_dir = Path(
        current_app.config["BASE_DIR"], "appmain/static/wdir", user)

    if not Path(working_dir).exists():
        Path(working_dir).mkdir(parents=True)
        Path(working_dir, "output").mkdir(parents=True)
    else:
        [p.unlink() for p in Path(working_dir).resolve().iterdir() if p.is_file()
         and "user.log" not in p.name]  # clean up

    return working_dir


@appmain_bp.route("/appmain", methods=["POST"])
def appmain():
    logger = current_app.logger

    user = current_user.username

    msg = f'[{mid}] --- @appmain_bp.route("/appmain") {user= } -----'
    print(dt.now().strftime(ftime) + " " + msg)
    logger.info(msg)

    # initialize
    command = request.form.get("command")  # or request.form["command"]
    selected_form = request.form.get("selected_form")
    groupname = request.form.get("groupname")
    print(f"[{mid}] {command= } {selected_form= } {groupname= }")

    record_to_be_processed = request.form.get("record_to_be_processed")
    print(f"[{mid}] {record_to_be_processed= }")
    executeParameters = request.form.get("executeParameters")
    print(f"[{mid}] {executeParameters= }")

    # appmain
    if command in ["submit_a_form"]:
        print(f"[{mid}] {command= }")

        file = request.files["data_file"]
        file_name = file.filename
        if ".xlsx" in file_name[-5:]:
            file_suffix = ".xlsx"
        elif ".csv" in file_name[-4:]:
            file_suffix = ".csv"
        else:
            alert = ("NG", "error: unsupported file type.")
            return render_template('area4Submit.html',
                                   user=current_user.username,
                                   message=alert[1],
                                   alert=alert[0])

        data = file.stream.read()

        # create control_data_dict
        if file_suffix == ".xlsx":
            alert, control_data_dict = utl.gen_control_data_dict(
                data, file_name)
        elif file_suffix == ".csv":
            alert, control_data_dict = utl.gen_control_data_dict_for_csv(
                data, file_name)
        else:
            control_data_dict = dict()
            alert = ("NG", "error: unsupported file type.")
        # print(f"[{mid}] {control_data_dict= }")

        if "NG" in alert[0]:
            return render_template('area4Submit.html',
                                   user=current_user.username,
                                   message=alert[1],
                                   alert=alert[0])
        # create input_data
        alert, input_data = utl.gen_input_data(data, control_data_dict)

        if "NG" in alert[0]:
            return render_template('area4Submit.html',
                                   user=current_user.username,
                                   message=alert[1],
                                   alert=alert[0])
        # dispatch command
        if "database_info_entry" in file_name:
            alert = cmd.database_info_entry(input_data)
        elif "group_info_entry" in file_name:
            alert = cmd.group_info_entry(input_data)
        elif "form_info_entry" in file_name:
            alert = cmd.form_info_entry(input_data)
        else:
            alert = cmd.write_form_items(input_data, control_data_dict)

        return render_template('area4Submit.html',
                               user=current_user.username,
                               message=alert[1],
                               alert=alert[0])

    elif command in ["get_a_list_of_forms"]:
        print(f"[{mid}] {command= }")

        items = cmd.get_a_list_of_forms()

        return render_template('area4Inquire.html',
                               user=current_user.username,
                               command=command,
                               items=items,
                               message="",
                               alert="OK")

    elif command in ["privilege"]:
        print(f"[{mid}] {command= }")

        items = cmd.get_a_list_of_forms_for_privilege()

        return render_template('area4Inquire.html',
                               user=current_user.username,
                               command=command,
                               items=items,
                               message="",
                               alert="OK")

    elif command in ["show_privilege_items"]:
        key, items = cmd.read_form_items_for_privilege(command, selected_form)
        items = [(i + 1, *item) for i, item in enumerate(items)]
        return render_template('area4InquireItems.html',
                               user=current_user.username,
                               command=command,
                               keys=key,
                               items=items,
                               selected_form=selected_form,
                               groupname=groupname,
                               message="",
                               alert="OK")

    elif command in ["signupusers"]:
        print(f"[{mid}] {command= }")

        items = cmd.get_a_list_of_signup_users()

        return render_template('area4Inquire.html',
                               user=current_user.username,
                               command=command,
                               items=items,
                               message="",
                               alert="OK")

    elif command in ["show_signup_users"]:
        key, items = cmd.read_signup_users()
        items = [(i + 1, *item) for i, item in enumerate(items)]
        return render_template('area4InquireItems.html',
                               user=current_user.username,
                               command=command,
                               keys=key,
                               items=items,
                               selected_form="userinfo",
                               groupname="",
                               message="",
                               alert="OK")

    elif command in ["show_the_first_item",
                     "show_items_updated_today",
                     "show_items_updated_in_a_week",
                     "show_all_the_items"]:
        print(f"[{mid}] {command= }")

        key, items = cmd.read_form_items(command, selected_form)

        # cope with too large items
        items_volume = len(key) * len(items)
        print(f"[{mid}]{items_volume= } ")
        if items_volume > 300_000:
            items = [(i + 1, *item) for i, item in enumerate(items[:500])]
            alert = (
                "NG", "error: Too large to show.  Show 500 items.  Please try to download csv file.")
        else:
            items = [(i + 1, *item) for i, item in enumerate(items)]
            alert = ("OK", "Done.")

        return render_template('area4InquireItems.html',
                               user=current_user.username,
                               command=command,
                               keys=key,
                               items=items,
                               selected_form=selected_form,
                               groupname=groupname,
                               message=alert[1],
                               alert=alert[0])

    elif command in ["drop_form_confirm"]:
        print(f"[{mid}] {command= }")

        items = list()
        for i, obj in enumerate(FormList.query.filter_by().all()):
            items.append([i + 1, obj.formname, obj.form_size,
                         obj.groupname, obj.update_at, obj.modified_by])
        items = [item for item in items if item[1] ==
                 selected_form and item[3] == groupname]

        return render_template("area4DeleteForm.html",
                               user=current_user.username,
                               items=items,
                               message="",
                               alert="OK")

    elif command in ["drop_form"]:
        print(f"[{mid}] {command= }")

        alert = cmd.drop_form(selected_form)

        if "OK" in alert[0]:
            items = cmd.get_a_list_of_forms()
            alert = ("OK", "Done.")
        else:
            pass
        return render_template("area4Inquire.html",
                               user=current_user.username,
                               command=command,
                               items=items,
                               message=alert[1],
                               alert=alert[0])

    elif command in ["delete_item"]:
        print(f"[{mid}] {command= }")

        cmd.delete_item(selected_form, record_to_be_processed)

        key, items = cmd.read_form_items("show_all_the_items", selected_form)

        # cope with too large items
        items_volume = len(key) * len(items)
        print(f"[{mid}]{items_volume= } ")
        if items_volume > 300_000:
            items = [(i + 1, *item) for i, item in enumerate(items[:500])]
            alert = (
                "NG", "error: Too large to show.  Show 500 items.  Please try to download csv file.")
        else:
            items = [(i + 1, *item) for i, item in enumerate(items)]
            alert = ("OK", "Done.")

        return render_template('area4InquireItems.html',
                               user=current_user.username,
                               command=command,
                               keys=key,
                               items=items,
                               selected_form=selected_form,
                               groupname=groupname,
                               message=alert[1],
                               alert=alert[0])

    elif command in ["delete_user"]:
        print(f"[{mid}] {command= }")

        alert = cmd.delete_user(selected_form, record_to_be_processed)

        if "OK" in alert[0]:
            key, items = cmd.read_signup_users()
            items = [(i + 1, *item) for i, item in enumerate(items)]
            alert = "OK", "Done."

        return render_template('area4InquireItems.html',
                               user=current_user.username,
                               command=command,
                               keys=key,
                               items=items,
                               selected_form="",
                               groupname="",
                               message=alert[1],
                               alert=alert[0])

    elif command in ["download_all_the_items"]:
        print(f"[{mid}] {command= }")

        command = "show_all_the_items"
        key, items = cmd.read_form_items(command, selected_form)

        # prepare working directory and output file name
        working_dir = prepare_working_dir(user)

        # digit = 15  # random sequence length
        # rnd = random.randrange(10 ** (digit - 1), 10 ** digit)  # to prevent browser cash

        # filename = "payload" + str(rnd) + ".zip"
        filename = "payload" + ".zip"

        output_file_name = Path(working_dir, filename)
        # output_file_name = Path(working_dir, "download", filename)

        # compress
        key = key[:-2]  # trim update_at and modified_by
        string = ",".join(key) + "\n"  # header line

        with io.StringIO() as fw:
            for item in items:
                for s in item[:-3]:  # trim update_at and modified_by
                    # ObjectID, datetime.datetime -> pure string
                    print(s, file=fw, end=",")
                print(item[-3], file=fw)  # write the last column without comma

            string += fw.getvalue()

        with zipfile.ZipFile(output_file_name, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
            # archive file name and string data
            new_zip.writestr(selected_form + '.txt', string)

        return render_template('area4Download.html',
                               user=current_user.username,
                               filename=filename,
                               message="Ready to download.",
                               alert="OK")

    elif command in ["download_database"]:
        print(f"[{mid}] {command= }")

        # get dbname
        # selected_form = file_name
        obj = FormInfo.query.filter_by(formname=selected_form).first()
        group = obj.groupname
        obj = GroupInfo.query.filter_by(groupname=group).first()
        dbname = obj.dbname

        # prepare working directory and output file name
        working_dir = prepare_working_dir(user)

        digit = 15  # length
        # to prevent browser cash
        rnd = random.randrange(10 ** (digit - 1), 10 ** digit)
        filename = "payload" + str(rnd) + ".zip"
        output_file_name = Path(working_dir, filename)

        # compress
        database_filename = Path(
            current_app.config["BASE_DIR"], "database", dbname + ".sqlite3")

        with zipfile.ZipFile(output_file_name, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
            new_zip.write(database_filename, arcname=dbname + ".sqlite3")

        return render_template('area4Download.html',
                               user=current_user.username,
                               filename=filename,
                               message="Ready to download.",
                               alert="OK")

    else:
        pass


@appmain_bp.route('/downloads/<path:filepath>')
def download_file(filepath):
    print(f"[{mid}] {filepath= }")  # ex.) "./download" + "/sampledata.zip"

    temp = filepath.split("/")
    # ex.) 'instance/wdir/sakura.suwa@example.com'
    file_dir = "/".join(temp[:-1])
    filename = temp[-1]  # ex.) 'payload320641879919542.zip'
    return send_from_directory(file_dir, filename, as_attachment=True, download_name=filename)
