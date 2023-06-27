##########################################################################################
# Written by Joshua Silver, jsilver@uow.edu.au                                           #
# Last Change: 2023-06-23                                                                #
#                                                                                        #
# Requires Python 3.8+: "$ sudo dnf install python38"                                    #
# Requires RClone: "$curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip #
##########################################################################################

import json
import logging
import os
import smtplib
import socket
import subprocess
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def pre_run_setup(data_dict):
    # Get start date and time for logs
    data_dict['run_data'] = {}
    now = time.time()
    data_dict['run_data']['start_time_val'] = now
    data_dict['run_data']['start_time_str'] = time.strftime("%Y%m%d-%H%M%S", time.localtime(now))
    if __debug__:
        print(f"Date Val: {data_dict['run_data']['start_time_val']}")
        print(f"Date Str: {data_dict['run_data']['start_time_str']}")
    # Get hostname
    data_dict['run_data']['hostname'] = socket.gethostname()
    if __debug__:
        print(f"Hostname: {data_dict['run_data']['hostname']}")
    # Get script name
    data_dict['run_data']['script_name'] = os.path.basename(__file__).split('.')[0]
    if __debug__:
        print(f"Script Name: {data_dict['run_data']['script_name']}")
    # Get base script path
    data_dict['run_data']['script_path'] = sys.path[0]
    if __debug__:
        print(f"Script Path: {data_dict['run_data']['script_path']}\n")
    # Check for config file
    if not os.path.exists(f"{data_dict['run_data']['script_path']}/config.json"):
        print("config.json file not found in script dir")
        sys.exit(1)


def read_config(data_dict):
    # Load config file into internal dictionary
    with open(f"{data_dict['run_data']['script_path']}/config.json", "r") as config_file:
        data_dict.update(json.load(config_file))
    if __debug__:
        print(f"{data_dict}\n")


# def check_config_file(data_dict):
#   Better checking to be added ... flag for any missing 'required' data.
#    if 'log_dir' not in data_dict['log_settings']:
#        print("\"log_dir\" not found in config file")
#        sys.exit(2)
#    if not data_dict['log_settings']['log_dir']:
#        print("\"log_dir\" empty in config file")
#        sys.exit(2)


def setup_logging(data_dict):
    # Check log dir exists
    data_dict['run_data']['log_path'] =\
        f"{data_dict['run_data']['script_path']}/{data_dict['log_settings']['log_dir']}/"
    if not os.path.exists(f"{data_dict['run_data']['log_path']}"):
        os.makedirs(f"{data_dict['run_data']['log_path']}")
    # TBD: Check for failed create, flag appropriately (prob a permissions issue)
    # Combine script log file info
    data_dict['run_data']['log_file'] = f"{data_dict['run_data']['log_path']}" +\
        f"{data_dict['run_data']['start_time_str']}-{data_dict['run_data']['script_name']}.log"
    logging.basicConfig(filename=data_dict['run_data']['log_file'],
                        level=data_dict['log_settings']['log_level'],
                        format="%(levelname)s: %(message)s")
    # Write basic info to log file
    logging.info(f"{data_dict['run_data']['script_name']} started on {data_dict['run_data']['hostname']}" +
                 f" at {data_dict['run_data']['start_time_str']}\n")


def do_transfer(data_dict):
    # Set 'success' flag
    data_dict['run_data']['run_status'] = "Success"
    # Loop through transfer tasks
    for i in data_dict['transfer_settings']['task_list']:
        # Skip any tasks that are turned off
        if i['rclone_action'] == "off":
            i['return_code'] = 0
            continue
        # Combine rclone log file info
        i['log_file'] = f"{data_dict['run_data']['log_path']}" +\
                        f"{data_dict['run_data']['start_time_str']}-rcloneLog_{i['description']}.log"
        # Build rclone command
        commandList = [data_dict['transfer_settings']['rclone_bin'], i['rclone_action'],
                       f"--config={data_dict['run_data']['script_path']}/rclone.conf",
                       f"--log-level={data_dict['transfer_settings']['rclone_log_level']}",
                       f"--log-file={i['log_file']}"]
        if i['rclone_max_duration_minutes'] != -1:
            commandList.append(f"--max-duration={i['rclone_max_duration_minutes']}m")
        if i['rclone_action'] == "copy":
            commandList.append("--create-empty-src-dirs")
        if i['rclone_action'] == "move":
            commandList.append("--delete-empty-src-dirs")
        if i['rclone_dry_run']:
            commandList.append("--dry-run")
        if i['rclone_num_transfers'] != -1:
            commandList.append(f"--transfers={i['rclone_num_transfers']}")
        if i['rclone_num_checkers'] != -1:
            commandList.append(f"--checkers={i['rclone_num_checkers']}")
        if i['rclone_filters'] == "on":
            if os.path.exists(f"{data_dict['run_data']['script_path']}/{i['description']}_filters.txt"):
                commandList.append(f"--filter-from={data_dict['run_data']['script_path']}/{i['description']}_filters.txt")
            else:
                commandList.append(f"--filter-from={data_dict['run_data']['script_path']}/filters.txt")
        if i['rclone_min_age_seconds'] != -1:
            commandList.append(f"--min-age={i['rclone_min_age_seconds']}s")
        if i['rclone_min_age_days'] != -1:
            commandList.append(f"--min-age={i['rclone_min_age_days']}d")
        if i['rclone_max_age_days'] != -1:
            commandList.append(f"--max-age={i['rclone_max_age_days']}d")
        if i['rclone_delete_excluded'] == "on":
            commandList.append("--delete-excluded")
            commandList.append("--delete-during")
        if i['rclone_action'] != "rmdirs":
            commandList.append(i['source'])
        commandList.append(i['destination'])
        if __debug__:
            print(f"RClone Command List: {commandList}")
        logging.info(f"RClone Command List for \"{i['description']}\": {commandList}")
        # Run rclone transfer command
        proc_ret = subprocess.run(commandList)
        logging.info(f"\"{i['description']}\" Return Code: {proc_ret.returncode}\n")
        i['return_code'] = proc_ret.returncode
        # Check for error
        if proc_ret.returncode == 0:
            # No Errors, RClone will have created an empty log file
            if not data_dict['log_settings']['keep_on_success']:
                os.remove(i['log_file'])
        else:
            # Flag Error (and keep log file).
            data_dict['run_data']['run_status'] = "Error"


def remove_old_logs(data_dict):
    # Loop through files in log folder
    for f in os.listdir(data_dict['run_data']['log_path']):
        f = data_dict['run_data']['log_path'] + f
        if __debug__:
            print(f"\nFile: {f}")
            print(f"mtime: {os.stat(f).st_mtime}")
        # Check file's modify time vs retention time
        if os.stat(f).st_mtime < data_dict['run_data']['start_time_val'] -\
                data_dict['log_settings']['remove_after_days'] * 86400:
            # Log and remove old files
            if os.path.isfile(f):
                logging.info(f"Removing old log file: {os.path.basename(f)}")
                os.remove(f)


def send_email(data_dict):
    if __debug__:
        print("Sending Email ...")
    msg = MIMEMultipart()
    # Set email fields
    msg['Subject'] = '%s: %s - %s' % (data_dict['run_data']['hostname'], data_dict['run_data']['script_name'],
                                      data_dict['run_data']['run_status'])
    msg['From'] = data_dict['email_settings']['from']
    msg['To'] = ','.join(data_dict['email_settings']['recipients'])
    # Load script log into email body
    with open(f"{data_dict['run_data']['log_file']}", "r") as fp:
        body = MIMEText(fp.read(), "plain")
        msg.attach(body)
    # Attach rclone log on error
    if data_dict['run_data']['run_status'] == "Error":
        for i in data_dict['transfer_settings']['task_list']:
            if i['return_code'] != 0:
                with open(f"{i['log_file']}", "r") as fp:
                    log = MIMEText(fp.read())
                    log.add_header('Content-Disposition', 'attachment', filename=os.path.basename(i['log_file']))
                    msg.attach(log)
    # Send email
    s = smtplib.SMTP(data_dict['email_settings']['smtp_server'])
    s.sendmail(data_dict['email_settings']['from'], data_dict['email_settings']['recipients'], msg.as_string())
    s.quit()


def main():
    data_dict = {}
    pre_run_setup(data_dict)
    read_config(data_dict)
    # TBD: check_config_file(data_dict)
    setup_logging(data_dict)
    do_transfer(data_dict)
    remove_old_logs(data_dict)
    # Check if we need to email anyone.
    if data_dict['email_settings']['send_on_success'] or data_dict['run_data']['run_status'] == "Error":
        send_email(data_dict)


if __name__ == '__main__':
    main()
