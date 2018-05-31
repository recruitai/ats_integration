import os
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


recruit_ai_url = os.getenv('RECRUIT_AI_URL')
recruit_ai_key = os.getenv('RECRUIT_AI_KEY')

class Candidate():

    def __init__(self):

        self.id = ""
        self.first_name = ""
        self.last_name = ""
        self.location = ""
        self.job_title = ""
        self.resume_file = ""
        self.encoded_resume = ""
        self.resume_words = ""
        self.date_entered = ""
        self.last_modified = ""
        self.company_id = ""
        self.address = ""
        self.city = ""
        self.state = ""
        self.postal_code = ""
        self.home_phone = ""
        self.mobile_phone = ""
        self.work_phone = ""
        self.current_salary = ""
        self.current_salary_ccy = ""
        self.desired_salary = ""
        self.desired_salary_ccy = ""
        self.email_address = ""
        self.industry = ""
        self.status = ""
        self.has_resume = ""
        self.default_currency = ""
        self.relationship_manager = ""
        self.referred_by = ""
        self.recruiter = ""
        self.months_guaranteed = ""
        self.client_position = ""
        self.annual_leave = ""
        self.resident_status = ""
        self.candidate_source = ""
        self.current_company = ""
        self.nationality = ""
        self.notice_period = ""
        self.desired_monthly_salary = ""
        self.experience  = ""
        self.education = ""
        self.desired_locations = ""
        self.employment_preference = ""
        self.experience_level = ""



class Position():

    def __init__(self):

        self.id = ""
        self.position_id = ""
        self.job_title = ""
        self.job_description = ""
        self.job_description_words = ""
        self.date_entered = ""
        self.last_modified = ""
        self.company_name = ""
        self.company_location = ""
        self.status = ""
        self.position_location = ""
        self.open_closed = ""


def write_candidate_data(candidates):

    for candidate in candidates:

        pdata = {}
        pdata["CandidateID"] = candidate.id
        pdata["FirstName"] = candidate.first_name
        pdata["LastName"] = candidate.last_name
        pdata["Resume"] = candidate.resume_words
        pdata["LastModifiedDate"] = candidate.last_modified
        pdata["CreatedDate"] = candidate.date_entered
        pdata["JobTitle"] = candidate.job_title
        pdata["InternalID"] = candidate.id

        attrs = {}
        attrs["Experience"] = candidate.experience
        attrs["EmploymentPreference"] = candidate.employment_preference
        attrs["CandidateSource"] = candidate.candidate_source
        attrs["Location"] = candidate.location

        pdata["Attributes"] = json.dumps(attrs)

        r = requests.post(recruit_ai_url + "/public/candidate",data=pdata, headers={"token":recruit_ai_key},verify=False)

        print(r.status_code, r.reason)


def write_position_data(positions):


    for position in positions:

        pdata = {}
        pdata["PositionID"] = position.id
        pdata["JobDescription"] = position.job_description_words
        pdata["JobTitle"] = position.job_title
        pdata["LastModifiedDate"] = position.last_modified
        pdata["CreatedDate"] = position.date_entered
        pdata["Company"] = position.company_name
        pdata["InternalID"] = position.id

        attrs = {}
        attrs["OpenClosed"] = position.open_closed
        attrs["Status"] = position.status
        attrs["Location"] = position.position_location

        pdata["Attributes"] = json.dumps(attrs)

        r = requests.post(recruit_ai_url + "/public/position",data=pdata, headers={"token":recruit_ai_key},verify=False)

        print(r.status_code, r.reason)
