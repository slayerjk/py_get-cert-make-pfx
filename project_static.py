"""
- logging settings
- date settings
- static initial project's data
"""

import logging
from datetime import datetime
import json
from os import path, mkdir

# COMMON DATA

# SCRIPT APPNAME(FOR SEND MAIL FUNCTION, LOGNAME, ETC)
appname = 'PKI-Auto'

# SCRIPT DATA DIR
'''
By default script uses script's location dir.
If you need custom path for script(sensitive) data
'''
script_dir = path.dirname(path.realpath(__file__))
data_files = f'{script_dir}/data_files'

# SET TIME TO
start_date_n_time = datetime.now()
start_date = start_date_n_time.strftime('%d-%m-%Y')

# LOGGING SECTION

# LOGS LOCATION
'''
By default script uses script's location dir.
'''
logs_dir = f'{script_dir}/logs'

# CHECK LOGS DIR EXIST/CREATE
if not path.isdir(logs_dir):
    mkdir(logs_dir)

# LOGS FORMAT
'''
logging_format: is for string of log representation
logging_datefmt: is for representation of %(asctime) param
'''
logging_format = '%(asctime)s - %(levelname)s - %(message)s'
logging_datefmt = '%d-%b-%Y %H:%M:%S'

# LOG FILEMODE
'''
a - for "append" to the end of file
w - create new/rewrite exist
'''
log_filemode = 'w'

# LOGS TO KEEP AFTER ROTATION
logs_to_keep = 30

# DEFINE LOG NAME
app_log_name = f'{logs_dir}/{appname}_{str(start_date)}.log'

# DEFINE LOGGING SETTINGS
logging.basicConfig(filename=app_log_name, filemode=log_filemode, level=logging.INFO,
                    format=logging_format, datefmt=logging_datefmt)


# MAILING DATA
mailing_data = f'{data_files}/mailing_data.json'
with open(mailing_data, encoding='utf-8') as file:
    data = json.load(file)
    smtp_server = data['smtp_server']
    smtp_port = data['smtp_port']
    smtp_login = data['smtp_login']
    smtp_pass = data['smtp_pass']
    smtp_from_addr = data['smtp_from_addr']
    mail_list_admins = data['list_admins']
    mail_list_users = data['list_users']

# VA PROJECT REGARDING DATA
csr_dir = f'{script_dir}/CSR'
results_dir = f'{script_dir}/results_{start_date}'

# template for PKI to use
template = 'Web client and server'

# pfx pass for making pfx file
pfx_pass = '123'

# OpenSSL binary path
openssl_bin = r'C:\Program Files\OpenSSL-Win64\bin\openssl.exe'

# certificate extension
cer_ext = 'crt'

# TEST
# script_data = f'{data_files}/data-test.json'

# PROD
script_data = f'{data_files}/data-prod.json'

with open(script_data, encoding='utf-8') as file:
    data = json.load(file)
    pki_url = data['pki-url']
    pki_user = data['pki-user']
    pki_pass = data['pki-pass']

# PROXY
proxies = {
    'http': None,
    'https': None
}
