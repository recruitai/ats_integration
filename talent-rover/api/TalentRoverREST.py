import json
import requests
import os
from urlparse import urlparse
from urlparse import parse_qs
import sys


import urllib2

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

register_openers()
opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))


import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

from subprocess import call


def make_get_request(url, token):

    done = False

    # while not done:
    # print(url)

    headers = {"Authorization": "Bearer " + token}

    response = requests.get(url, headers=headers, timeout=20)
    #print(base_url + url)
    # print(response.text)
    jres = response.json()
    response.close()
    done = True
    return jres


def make_request(url,token,data=""):

    # print(url)
    #headers = {"Content-type": "application/json;"}
    headers = {}
    if token is not None:
        headers = {"Authorization": "Bearer " + token,"Content-Type":"application/json"}
    response = requests.post(url, timeout=10, data=json.dumps(data), headers=headers)
    # print(response.text)
    jres = response.json()
    # print(jres)
    response.close()

    return jres

def make_raw_request(url, token):

    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers, timeout=20)
    response.close()

    return response.content


def make_multipart_request(url, token, filename, data):


    file_type = ".pdf"

    fname =  filename.split("/")[-1]

    if len(fname) > 4:
        if fname[-4] == ".":
            file_type = fname[-3:]

    if len(fname) > 5:
        if fname[-5] == ".":
            file_type = fname[-4:]


    part1 = '--boundary_string\n\
    Content-Disposition: form-data; name="entity_document";\n\
    Content-Type: application/json\n\n\
    {\n\
        "Description" : "{0}",\n\
        "Name" : "{1}",\n\
        "ParentId": "{2}"\n\
    }\n\n'

    part1 = part1.replace("{0}",data["Description"])
    part1 = part1.replace("{1}",data["Name"])
    part1 = part1.replace("{2}",data["ParentId"])

    part2 = '--boundary_string\n\
    Content-Type: application/{0}\n\
    Content-Disposition: form-data; name="Body"; filename="{1}"\n\n'

    part2 = part2.format(file_type, data["Name"])

    part3 = '\n\n--boundary_string--'

    with open(filename) as bf:

        with open("temp/request.json","w") as rfile:
            rfile.write(part1)
            rfile.write(part2)
            rfile.write(bf.read())
            rfile.write(part3)

    request_curl = 'curl {0} -H \'Authorization: Bearer {1}\' -H \'Content-Type: multipart/form-data; boundary=\"boundary_string\"\' --data-binary @temp/request.json'.format(url,token)

    with open("temp/request.bash","w") as rfile:
        rfile.write(request_curl)

    call("bash " + dir_path + "/temp/request.bash > "+ dir_path + "/temp/result.txt",shell=True)

    with open("temp/result.txt") as rfile:
        res = json.loads(rfile.read())
    return res


class TalentRoverREST:

    def __init__(self, app_path):

        #for multipart requests
        if not os.path.exists("temp"):
            os.mkdir("temp")

        credentials = json.load(open(app_path + '/credentials.json'))

        self.instance_url = credentials["instance_url"]

        if not self.instance_url.endswith("/"):
            self.instance_url+="/"

        self.api_version = "v43.0"
        self.auth_url = "https://login.salesforce.com/services/"
        self.base_rest_url = self.instance_url + "services/data/" + self.api_version + "/"

        self.grant_type = "password"
        self.redirect_uri = "https://login.salesforce.com/services/oauth2/success"



        self.username = credentials["username"]
        self.password = credentials["password"]
        self.client_id = credentials["client_id"]
        self.client_secret = credentials["client_secret"]

        self.authorization_url = self.auth_url + "oauth2/token?grant_type=password&client_id={0}&client_secret={1}&username={2}&password={3}"

        self.authorization_url = self.authorization_url.format(self.client_id, self.client_secret, self.username, self.password)

        self.app_path = app_path

        self.rest_url = self.base_rest_url
        self.rest_token = None

        self.api_limit_threshold = 1000 #if number of API calls left < this then exit...

        #add some breathing space as checking the actual API limit drains the limit
        #so we only check every 100 calls
        self.api_limit_threshold+=100

        self.estimate_remianing = 0

        #track number of calls to API
        self.session_calls = 0
        self.estimate_remaining = self.api_limit_threshold

        self.update_rest_token()


        exceeded, remaining = self.check_api_limit_exceeded()

        print(exceeded, remaining)

        if remaining <= self.api_limit_threshold:
            sys.exit("API limit threshold exceded, stop.")
        else:
            self.estimate_remaining = remaining - self.api_limit_threshold

    def increment_session_calls(self):
        self.session_calls+=1
        print("Session calls:", self.session_calls, "Estimate remaining",self.estimate_remaining)
        if self.session_calls >= self.estimate_remaining:
            sys.exit("API limit threshold exceded, stop.")

        #update current limits every n session calls
        if self.session_calls % 100==0:
            exceeded, remaining = self.check_api_limit_exceeded()
            if remaining <= self.api_limit_threshold:
                sys.exit("API limit threshold exceded, stop.")
            else:
                self.estimate_remaining = remaining - self.api_limit_threshold

    def update_rest_token(self):

        auth_error = False
        rest_token = ""

        print(self.app_path)
        # 2. Get an access token

        auth_token_url = self.auth_url + "oauth2/token?grant_type=password&client_id={0}&client_secret={1}&username={2}&password={3}"
        auth_token_url = auth_token_url.format(self.client_id, self.client_secret, self.username, self.password)

        access_token_details = make_request(auth_token_url,None)

        if "access_token" in access_token_details:
            self.rest_token = access_token_details["access_token"]
            print("rest token",self.rest_token)
        else:
            print(access_token_details)
            print("Unable to authorize")
            auth_error = True

        self.increment_session_calls()


    def check_api_limit_exceeded(self):

        #use sparingly as this call counts toward the limit itself :0
        result = make_get_request(self.base_rest_url + "limits",self.rest_token)
        remaining = result["DailyApiRequests"]["Remaining"]

        self.increment_session_calls()

        if remaining < self.api_limit_threshold:
            return True, remaining
        else:
            return False, remaining


    def make_rest_call(self, url):

        if self.rest_token == None:
            self.update_rest_token()

        rurl = self.rest_url + url

        print(rurl)
        result = make_get_request(rurl,self.rest_token)
        self.increment_session_calls()
        if "errorCode" in result:
            if "errorMessageKey" in result:
                if result["errorMessageKey"] == "errors.authentication.invalidRestToken":
                    self.update_rest_token()
                    rurl = url
                    return self.make_rest_call(rurl,self.rest_token)
        else:
            return result

    def make_rest_call_post(self, url, data):

        rurl = self.rest_url + url

        result = make_request(rurl,self.rest_token,data)
        # print(result)
        self.increment_session_calls()

        return result

    def make_rest_call_raw(self, url):

        if self.rest_token == None:
            #os.remove(self.app_path + '/access_token_details.json')
            self.update_rest_token()

        rurl = self.rest_url + url

        #print(rurl)
        result = make_raw_request(rurl,self.rest_token)
        self.increment_session_calls()
        if "errorCode" in result:
            if result["errorCode"] == "INVALID_SESSION_ID":
                self.update_rest_token()
                rurl = url
                return self.make_rest_call_raw(rurl,self.rest_token)
        else:
            return result


    def make_rest_multipart_request(self, url, filename, data):

        if self.rest_token == None:
            #os.remove(self.app_path + '/access_token_details.json')
            self.update_rest_token()

        rurl = self.rest_url + url

        result = make_multipart_request(rurl,self.rest_token,filename,data)

        self.increment_session_calls()
        if "errorCode" in result:
            if result["errorCode"] == "INVALID_SESSION_ID":
                self.update_rest_token()
                rurl = url
                return self.make_rest_multipart_request(rurl,self.rest_token,filename,data)
        else:
            return result


if __name__ == '__main__':

    trRest = TalentRoverREST(os.getenv('CREDENTIAL_LOCATION'))
    trRest.update_rest_token()
