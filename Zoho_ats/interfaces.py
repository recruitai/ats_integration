import os
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

recruit_ai_url = os.getenv('RECRUIT_AI_URL')
recruit_ai_key = os.getenv('RECRUIT_AI_KEY')

class Candidate():

    def __init__(self):#populate all of these

        self.id = ""#CANDIDATEID
        self.first_name = ""#First Name
        self.last_name = ""#Last Name
        self.email = ""##Email
        self.mobile = ""#Mobile
        self.street = "" #Street
        self.city = "" ##City
        self.state = "" #State
        self.zip_code = "" #Zip Code
        self.country = "" #Country
        self.expeirence = ""#Experience in Years
        self.current_employer = ""#Current Employer
        self.current_job = ""#Current Job Title
        self.skills = ""#Skill Set
        self.expected_salary = ""#Expected Salary
        self.current_salary = ""#Current Salary
        self.additional_info = ""#Additional Info
        self.created_by = ""#Created By
        self.modified_by = ""#MODIFIEDBY might self generate
        self.created_time = ""#Created Time
        self.updated_on = ""#Updated On
        self.salutation = ""#Salutation
        self.last_activity = ""#Last Activity ?? skip
        #self.cand_owner = ""#Candidate Owner
        self.source = ""#Source
        self.email_opt_out = ""#Email Opt Out
        self.is_locked = ""#Is Locked
        self.unqualified = ""#Unqualified
        self.attachment = ""#Attachment Present
        self.status = ""#Candidate Status


class Position():

    def __init__(self):

        self.id = ""
        self.job_title = ""
        self.job_type = ""
        self.last_activity = ""
        self.job_status = ""
        self.date_opened = ""
        self.client_name = ""
        self.city = "" #maybe combine city,state,country into self.company_location or soemthing?
        self.state = ""
        self.country = ""
        self.industry = ""
        self.modified_by = ""
        self.created_time = ""
        self.modified_time = ""
        self.work_experience = ""
        self.salary = ""
        self.description = ""
        self.attachment = ""
        self.zip_code = ""


def write_candidate_data(candidates):

    for candidate in candidates:

        pdata = {}
        pdata["CANDIDATEID"] = candidate.id
        pdata["First Name"] = candidate.first_name
        pdata["Last Name"] = candidate.last_name
        pdata["Resume"] = 

        #populate the rest

        r = requests.post(recruit_ai_url + "/public/candidates",data=pdata,headers={"token":recruit_ai_key},verify=False)

        print(r.status_code, r.reason)

def write_position_data(positions):

    for position in positions:

        pdata = {}
        pdata["JOBOPENINGID"] = position.id
        pdata["Posting Title"] = position.job_title

        r = requests.post(recruit_ai_url + "/public/positions",data=pdata,headers={"token":recruit_ai_key},verify=False)

        print(r.status_code, r.reason)
