import json
import sys
from BullhornREST import BullhornREST
import base64, M2Crypto
import os
#initialise a bullhorn instance
#pass API details
app_path = os.environ.get('CREDENTIAL_LOCATION')

def write_credentials(username,password,client_id,client_secret):

    creds = {}
    creds["username"] = username
    creds["password"] = password
    creds["client_id"] = client_id
    creds["client_secret"] = client_secret

    with open(app_path + '/credentials.json', 'w') as outfile:
        json.dump(creds, outfile)

    rest = BullhornREST(app_path)
    rest.update_rest_token()
    corp_code = rest.get_corp_code()
    quark_token = base64.b64encode(M2Crypto.m2.rand_bytes(16))

    comps = {}
    comps["corp_code"] = corp_code
    comps["quark_token"] = quark_token
    comps["app_url"] = app_url

    with open(app_path + '/components.json', 'w') as outfile:
        json.dump(comps, outfile)

    print("Success.")

    #print(app_url + "/bh_pos.html?bh=" + quark_token)
    #metas = rest.make_rest_call("meta/Candidate?fields=*&meta=full")

    #print(metas)


if __name__ == '__main__':

    #create_custom_components()
    username = sys.argv[1]
    password = sys.argv[2]
    client_id = sys.argv[3]
    client_secret = sys.argv[4]

    write_credentials(username,password,client_id,client_secret,app_url)
