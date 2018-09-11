import json
import requests
import os
import sys
from flatten_dict import flatten

def make_get_request(url):
    done = False

    headers = {"Content-type": "applications/json;"}
    response = requests.get(url, headers = headers, timeout = 5)

    jres = response.json()
    response.close()
    done = True

    result = jres["response"]["result"]
    return result#messy due to nested dictionary should flatten

def make_get_request_txt(url):#get the initial token (Errors out if its JSON)
    done = False

    response = requests.get(url, timeout=5)

    text = response.text
    response.close()
    done = True
    return text

def make_request(url,data=""):

    response = requests.post(url,timeout=10,data=data)
    jres = jres.response()
    response.close()
    return jres


class ZohoREST:

    def __init__(self,app_path):

        self.auth_url = "https://accounts.zoho.com/"#update
        self.base_rest_url = "https://recruit.zoho.com/"#update

        credentials = json.load(open(app_path + '/credentials.json'))#done

        self.username = credentials["username"]#self.username
        self.password = credentials["password"]#self.password

        self.authorization_url = self.auth_url + "apiauthtoken/nb/create?SCOPE=ZohoRecruit/recruitapi&EMAIL_ID={0}&PASSWORD={1}"#update
        self.authorization_url = self.authorization_url.format(self.username,self.password)

        self.app_path = app_path

        self.rest_url = ""
        self.rest_token = None#might need to update_rest_token


    def update_rest_token(self):

        auth_error = False
        rest_token = ""


        #2. Get an access token
        if not os.path.exists(self.app_path + '/access_token_details.json'):

            print("access_token_details doesn't exist...")
            print("Creating access_token_details.json file...")#test

            auth_token_url = self.auth_url + "apiauthtoken/nb/create?SCOPE=ZohoRecruit/recruitapi&EMAIL_ID={0}&PASSWORD={1}"
            auth_token_url = auth_token_url.format(self.username,self.password)

            access_token_details = make_get_request_txt(auth_token_url)

            if "FALSE" not in access_token_details:

                #3. Store the token
                with open(self.app_path + '/access_token_details.json', 'w') as outfile:
                    outfile.write(access_token_details)

                with open(self.app_path + '/access_token_details.json', 'r') as read_outfile:#maybe make this a function
                    result = read_outfile.read().strip("AUTHTOKEN=").split('\n')
                    access_tok = result[2].lower()#assigning lowercase authtoken=xyz
                    self.rest_token = access_tok

            else:
                print(access_token_details)
                print("Unable to authorize possibly too many tokens.\n")
                auth_error = True

        #checks if already have the access token so we dont need to create a enw one.
        elif os.path.exists(self.app_path + '/access_token_details.json'):

            with open(self.app_path + '/access_token_details.json', 'r') as read_outfile:#lambda??
                contents = read_outfile.read()

                if "FALSE" not in contents:
                    with open(self.app_path + '/access_token_details.json', 'r') as read_outfile:
                        result = read_outfile.read().strip("AUTHOKEN=").split('\n')
                        access_tok = result[2].lower()
                        self.rest_token = access_tok

                else:
                    print(contents)
                    print("Unable to authorize possibly too many tokens.\n")
                    print("If you need to generate a new token just delete the existing access_token_details.json file.\n")
                    auth_error = True

        else:

            #Create new authtoken if there is no access_token_details.json
            print("Creating new access token...")

            url = self.auth_url + "apiauthtoken/nb/create?SCOPE=ZohoRecruit/recruitapi&EMAIL_ID={0}&PASSWORD={1}"
            url = url.format(self.username, self.password)

            access_token_details = make_get_request_txt(url)
            print(access_token_details)

            if "AUTHTOKEN" in access_token_details:
                with open(self.app_path + '/access_token_details.json', 'w') as outfile:
                    outfile.write(access_token_details)

                with open(self.app_path + '/access_token_details.json', 'r') as read_outfile:
                    result = read_outfile.read().strip("AUTHTOKEN=").split('\n')
                    access_tok = result[2].lower()#assigning lowercase authtoken=xyz

                    auth_error = False
            else:
                print("Unable to authorize")
                auth_error = True

        if not auth_error:#Just for testing the call

            print("Testing REST..")
            url = self.base_rest_url + "recruit/private/json/Candidates/getRecords?{0}&scope=recruitapi"
            url = url.format(access_tok)
            rest_details = make_get_request(url)

            self.rest_token = access_tok

            #?return?


    def make_rest_call(self,url):#add model
        #some token checks would be nice here or in zoho api?
        #url = "recruit/private/json/{0}/getRecords?"

        rurl = self.base_rest_url + url + self.rest_token + "&scope=recruitapi"
        print(rurl)
        #result = url.format(access_tok)

        result = make_get_request(rurl)

        #print(result)#this works  but lets try to make it flat
        if "error" in result:#needs to be fixed
            if "code" in result:
                if result["code"] == result["message"]:
                    self.update_rest_token()
                    rurl = url
                    return self.make_rest_call(rurl)
        else:
            return result


    def make_rest_call_post(self,url,data):

        rurl = self.rest_url + url + "&BhRestToken=" + self.rest_token

        result = make_request(rurl,data)
        #print(result)

        return result
