__author__ = "Arvind Rosunee"
__copyright__ = "Copyright (C) 2020 Arvind Rosunee"
__license__ = "MIT License"
__version__ = "1.0"

import requests
from datetime import datetime
import tarfile
import os

requests.packages.urllib3.disable_warnings()

# Device details
ip_address = '10.1.1.1'
username = 'a_username'
password = 'a_password'

# Compose file names
date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
backup_file_path = 'backup_' + ip_address.replace(".", "_") + '_' + date_time + '.txt'
tar_backup_file_path = 'backup_' + ip_address.replace(".", "_") + '_' + date_time + '.tar'

# Payload and URls
payload = {'Username': username, 'Password': password}
url_login = 'https://{}/rest/login'.format(ip_address)
url_logout = 'https://{}/rest/logout'.format(ip_address)

# Authenticate to SBC
login_response = None
try:
    login_response = requests.request("POST", url_login, verify=False, data=payload)
except Exception as e:
    print('Login failed with error message {}'.format(e))

# Save the Session Token Cookie from the response header
cookie = None
if login_response.status_code == 200:
    print('Logged in to SBC: {}'.format(ip_address))
    headers_response = login_response.headers.__dict__
    cookie = headers_response['_store']['set-cookie'][1]

# Backup the gateway
if cookie:
    url_backup = 'https://{}/rest/system?action=backup'.format(ip_address)

    headers = {
        'COOKIE': cookie
    }
    backup_response = requests.request("POST", url_backup,  verify=False, headers=headers)

    # Save backup to text file
    if backup_response.status_code == 200:
        with open(backup_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(backup_response.text)

        # compress text file to a tar file
        with tarfile.open(tar_backup_file_path, "w:gz") as tar:
            tar.add(backup_file_path)

        # remove the text file
        os.remove(backup_file_path)
        print('Backed up SBC: {}'.format(ip_address))

        # logout from SBC and close the connection
        logout_response = requests.request("POST", url_logout, verify=False, headers=headers)
        print('Close connection to SBC: {}'.format(ip_address))
        print()

    else:
        print('Backup failed with response code: {}'.format(backup_response.status_code))
