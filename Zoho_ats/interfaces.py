import os
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

recruit_ai_url = os.getenv('RECRUIT_AI_URL')
recruit_ai_key = os.getenv('RECRUIT_AI_KEY')

class Candidate():

    def __init__(self):#populate all of these

        self.id = ""
        self.first_name = ""

class Position():

    def __init__(self):

        self.id = ""
        self.job_title = ""

def write_candidate_data(candidates):

    for candidate in candidates:

        pdata = {}
        pdata["CANDIDATEID"] = candidate.id
        pdata["First Name"] = candidate.first_name

        r = requests.post(recruit_ai_url + "/public/candidates",data=pdata,headers={"token":recruit_ai_key},verify=False)

        print(r.status_code, r.reason)

def write_position_data(positions):

    for position in positions:

        pdata = {}
        pdata["JOBOPENINGID"] = position.id
        pdata["Posting Title"] = position.job_title

        r = requests.post(recruit_ai_url + "/public/positions",data=pdata,headers={"token":recruit_ai_key},verify=False)

        print(r.status_code, r.reason)
