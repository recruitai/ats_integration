import json
import sys
from zohoREST import ZohoREST
import base64, M2Crypto
import os

app_path = os.environ.get('CREDENTIAL_LOCATION')

def write_credentials(username,password):
    print(app_path)
    creds = {}
    creds["username"] = username
    creds["password"] = password

    with open(app_path + '/credentials.json', 'w') as outfile:
        json.dump(creds, outfile)

    rest = ZohoREST(app_path)
    rest.update_rest_token()

    quark_token = base64.b64encode(M2Crypto.m2.rand_bytes(16))

    comps = {}
    comps["quark_token"] = quark_token

    with open(app_path + '/components.json', 'w') as outfile:
        json.dump(comps, outfile)

    print("Success.")


if __name__ == '__main__':

    username = sys.argv[1]
    password = sys.argv[2]

    write_credentials(username,password)
