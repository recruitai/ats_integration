import json
import requests
import os
from urlparse import urlparse
from urlparse import parse_qs

def make_get_request(url):

    done = False

    #while not done:
    #print(url)

    headers = {"Content-type": "application/json;"}
    response = requests.get(url, headers=headers,timeout=5)
    #print(base_url + url)
    #print(response.text)
    jres = response.json()
    response.close()
    done = True
    return jres

def make_request(url,data=""):

    #print(url)
    #headers = {"Content-type": "application/json;"}
    response = requests.post(url,timeout=10,data=data)
    #print(response.text)
    jres = response.json()
    #print(jres)
    response.close()

    return jres


class BullhornREST:

    def __init__(self,app_path):

        self.auth_url = "https://auth.bullhornstaffing.com/"
        self.base_rest_url = "https://rest.bullhornstaffing.com/"

        credentials = json.load(open(app_path + '/credentials.json'))

        self.username = credentials["username"]
        self.password = credentials["password"]
        self.client_id = credentials["client_id"]
        self.client_secret = credentials["client_secret"]

        self.authorization_url = self.auth_url + "oauth/authorize?client_id={0}&response_type=code&username={1}&password={2}&action=Login"
        self.authorization_url  = self.authorization_url.format(self.client_id,self.username,self.password)

        self.app_path = app_path

        self.rest_url = ""
        self.rest_token = None

    def update_rest_token(self):

        auth_error = False
        rest_token = ""

        print(self.app_path)
        #2. Get an access token
        if not os.path.exists(self.app_path + '/access_token_details.json'):

            print("access_token_details doesn't exist...")

            response = requests.get(self.authorization_url,timeout=5)

            parsed_url = urlparse(response.url)
            qs = parse_qs(parsed_url.query)

            if "code" in qs:

                auth_token_url = self.auth_url + "oauth/token?grant_type=authorization_code&code={0}&client_id={1}&client_secret={2}"
                auth_token_url = auth_token_url.format(qs["code"][0],self.client_id,self.client_secret)

                access_token_details = make_request(auth_token_url)

                if "error" not in access_token_details:

                    #3. Store the refresh token
                    with open(self.app_path + '/access_token_details.json', 'w') as outfile:
                        json.dump(access_token_details, outfile)

                    access_tok = access_token_details["access_token"]
                else:
                    print(access_token_details)
                    print("Unable to authorize")
                    auth_error = True
                
        else:

            #6a. Get refresh token
            access_token_details = json.load(open(self.app_path + '/access_token_details.json'))

            print("access_token_details exists...")
            print(access_token_details)
            #{u'error_description': u'Invalid, expired, or revoked refresh token.', u'error': u'invalid_grant'}
            refresh_token = access_token_details["refresh_token"]
            #6b. Get new access token and store new refresh token
            url = self.auth_url + "oauth/token?grant_type=refresh_token&refresh_token={0}&client_id={1}&client_secret={2}"
            url = url.format(refresh_token,self.client_id,self.client_secret)
            refresh_details = make_request(url)
            print(refresh_details)
            if "access_token" in refresh_details:
                access_tok = refresh_details["access_token"]
                with open(self.app_path + '/access_token_details.json', 'w') as outfile:
                    json.dump(refresh_details, outfile)
            else:
                print("Unable to authorize")
                auth_error = True

    #4. Get a rest token
        if not auth_error:

            url = self.base_rest_url + "/rest-services/login?version=2.0&access_token={0}"
            url = url.format(access_tok)
            rest_details = make_request(url)

            #here set rest url and extract token

            self.rest_token = rest_details["BhRestToken"]
            self.rest_url = rest_details["restUrl"]

    def get_corp_code(self):

        paths = self.rest_url.split("/")
        if len(paths) > 2:
            return paths[-2]

    def make_rest_call(self,url):


        if self.rest_token == None:
            os.remove(self.app_path + '/access_token_details.json')
            self.update_rest_token()

        rurl = self.rest_url + url + "&BhRestToken=" + self.rest_token
        result = make_get_request(rurl)
        if "errorCode" in result:
            if "errorMessageKey" in result:
                if result["errorMessageKey"] == "errors.authentication.invalidRestToken":
                    self.update_rest_token()
                    rurl = url + "&BhRestToken=" + self.rest_token
                    return self.make_rest_call(rurl)
        else:
            return result


    def make_rest_call_post(self,url,data):

        rurl = self.rest_url + url + "&BhRestToken=" + self.rest_token

        result = make_request(rurl,data)
        #print(result)

        return result
