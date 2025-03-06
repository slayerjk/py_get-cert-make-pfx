#!/usr/bin/env python3
import glob
import os.path
from tempfile import TemporaryFile
from time import perf_counter
from playwright.sync_api import sync_playwright
import urllib3

# IMPORT PROJECTS PARTS
from project_static import (
    appname,
    start_date_n_time,
    logging,
    logs_dir,
    logs_to_keep,
    data_files,
    pki_url,
    pki_user,
    pki_pass,
    script_data,
    results_dir,
    csr_dir,
    template,
    cer_ext,
    pfx_pass,
    openssl_bin
)

from app_scripts.project_helper import files_rotate, check_create_dir, func_decor, check_file

from app_scripts.app_functions import (
    create_cert,
    make_pfx
)

# MAILING IMPORTS(IF YOU NEED)
# from project_static import smtp_server, smtp_port, smtp_from_addr, mail_list_users
# from app_scripts.project_mailing import send_mail_report

# DISABLE SSL WARNINGS
urllib3.disable_warnings()

# STARTED TEMP FILE FOR USER REPORT
user_report = TemporaryFile(mode='w+t')

# SCRIPT STARTED ALERT
logging.info(f'{appname}: SCRIPT WORK STARTED')
logging.info(f'Script Starting Date&Time is: {str(start_date_n_time)}')
logging.info('----------------------------\n')


# START PERF COUNTER
start_time_counter = perf_counter()


# CHECK DATA DIR EXIST/CREATE
func_decor(f'checking {data_files} dir exists and create if not')(check_create_dir)(data_files)


# CHECKING DATA DIRS & FILES
func_decor(f'checking {script_data} file exist', 'crit')(check_file)(script_data)
func_decor(f'checking {results_dir} dir exist/create', 'crit')(check_create_dir)(results_dir)
func_decor(f'checking {csr_dir} dir exist/create', 'crit')(check_create_dir)(csr_dir)


# CHECK MAILING DATA EXIST(IF YOU NEED MAILING)
# func_decor(f'checking {mailing_data} exists', 'crit')(check_file)(mailing_data)

"""
OTHER CODE GOES HERE
"""
user_report.write(f'{appname}: {str(start_date_n_time)}\n')
user_report.write('----------------------------\n')

# ITERATING OVER CSR DIRS
# getting cn_name(dir's name inside CSR DIRS) and it's path
total_cn_to_process = []
failed_cn_to_process = []
successfully_processed = []
pfx_failed = []
for csr_dir_path in os.scandir(csr_dir):
    csr_file_path = ""
    key_file_path = ""
    cer_file_path = ""

    cn_name = os.path.basename(csr_dir_path)
    cn_path = csr_dir_path.path
    total_cn_to_process.append(cn_name)
    # getting csr file path inside csr dir
    for file in glob.iglob(f'{cn_path}/*.csr'):
        csr_file_path = file
        break
    # getting key file path inside csr dir
    for file in glob.iglob(f'{cn_path}/*.key'):
        key_file_path = file
        break
    # skip this cn if there is no csr or key found
    if not csr_file_path or not key_file_path:
        logging.warning(f"no CSR or KEY file found in {cn_path}, skipping")
        failed_cn_to_process.append(cn_name)
        continue

    # CREATING CERTS
    logging.info(f'STARTED: creating certs for {cn_name}\n')
    downloaded_certs_pathes = []
    with sync_playwright() as playwright:
        try:
            cert_path = create_cert(
                pki_url,
                pki_user,
                pki_pass,
                csr_file_path,
                template,
                cn_name,
                cer_ext,
                cn_path,
                playwright
            )
        except Exception as e:
            logging.warning(f'FAILED: creating cert for {cn_name}, \n{e}, \nskipping\n')
        else:
            successfully_processed.append(cn_name)
            logging.info(f'DONE: creating cert for {cn_name}\n')

    # getting key file path inside csr dir
    for file in glob.iglob(f'{cn_path}/*.crt'):
        cer_file_path = file
        break
    if not cer_file_path:
        logging.warning(f"no CRT file found in {cn_path}, skipping")
        failed_cn_to_process.append(cn_name)
        continue

    # making pfx
    try:
        make_pfx(openssl_bin, cn_name, cer_file_path, key_file_path, cn_path, pfx_pass)
    except Exception as e:
        logging.warning(f'FAILED: to create PFX file for {cn_name}, \n{e}, skipping')
        pfx_failed.append(cn_name)
        continue

# report
if len(failed_cn_to_process) > 0:
    logging.warning(f'failures for: {failed_cn_to_process}')
if len(successfully_processed) == len(total_cn_to_process):
    logging.info('all CNs processed successfully!')
if len(pfx_failed) > 0:
    logging.warning(f'failures for PFX: {pfx_failed}')
# logging.info(f'processed CNs:\n{successfully_processed}')

# SENDING FINAL USER REPORT
user_report.seek(0)
# (func_decor('sending user report')(send_mail_report)
#  (appname, mail_list_users, smtp_from_addr, smtp_server, smtp_port, mail_body=user_report.read()))


# POST-WORK PROCEDURES

# FINISH JOBS
logging.info('#########################')
logging.info('SUCCEEDED: Script job done!')
logging.info(f'Estimated time is: {perf_counter() - start_time_counter}')
logging.info('----------------------------\n')
files_rotate(logs_dir, logs_to_keep)

# (func_decor('sending Script Final LOG')(send_mail_report)
#     (appname, mail_list_admins, smtp_from_addr, smtp_server, smtp_port, log_file=app_log_name, report='f'))
