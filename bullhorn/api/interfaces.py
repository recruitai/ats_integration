import os
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

class Interview():

    def __init__(self):

        self.id = ""
        self.job_id = ""
        self.candidate_id = ""
        self.company_id = ""
        self.interview_status = ""
        self.interview_type = ""
        self.date_entered = ""
        self.last_modified = ""
        self.company_name = ""
        self.appointment_date = ""
        self.arranged_date = ""

class Placement():

    def __init__(self):

        self.id = ""
        self.job_id = ""
        self.candidate_id = ""
        self.company_id = ""
        self.date_entered = ""
        self.last_modified = ""
        self.company_name = ""
        self.placement_date = ""
        self.placed_by = ""


class Company():

    def __init__(self):

        self.id = ""
        self.company_name = ""
        self.country = ""


def write_candidate_data(candidates):


    #"https://localhost:1111/public/candidate"

    #headers token 123456
    #[{"key":"Content-Type","value":"application/x-www-form-urlencoded","description":""}]

    #{"Location":"Tokyo","CandidateSource":"Indeed","EmploymentPreference":"Contract","Experience":"Level1"}
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

        r = requests.post("https://localhost:1111/public/candidate",data=pdata, headers={"token":"123456"},verify=False)

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

        r = requests.post("https://localhost:1111/public/position",data=pdata, headers={"token":"123456"},verify=False)

        print(r.status_code, r.reason)


    #validate_data = pd.read_csv(target_dir + "/position_index_data.tsv", dtype=object, header=0,  delimiter="\t", quotechar='"' , lineterminator='\n', quoting=3, skipinitialspace=True)
    #print("loaded {0} records.".format(validate_data.count()))

def write_interview_drop(interviews,drop_tag,drop_location):

    target_dir = drop_location + drop_tag
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    f = open(target_dir + "/interview_index_data.tsv", "w")
    f.write("ID\tJobId\tCandidateId\tAppointmentDate\tArrangedDate\tCompanyName\tInterviewType\tInterviewStatus\n")

    for interview in interviews:
        f.write("\"")
        f.write(interview.id)
        f.write("\"\t\"")
        f.write(interview.job_id)
        f.write("\"\t\"")
        f.write(interview.candidate_id)
        f.write("\"\t\"")
        f.write(interview.appointment_date)
        f.write("\"\t\"")
        f.write(interview.arranged_date)
        f.write("\"\t\"")
        f.write(interview.company_name)
        f.write("\"\t\"")
        f.write(interview.interview_type)
        f.write("\"\t\"")
        f.write(interview.interview_status)
        f.write("\"")
        f.write("\n")

    f.close()

    validate_data = pd.read_csv(target_dir + "/interview_index_data.tsv", dtype=object, header=0,  delimiter="\t", quotechar='"' , lineterminator='\n', quoting=3, skipinitialspace=True)
    print("loaded {0} records.".format(validate_data.count()))

def write_placement_drop(placements,drop_tag,drop_location):

    target_dir = drop_location + drop_tag
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    f = open(target_dir + "/placement_index_data.tsv", "w")
    f.write("ID\tJobId\tCandidateId\tCompanyId\tCompanyName\tPlacementDate\tPlacedBy\n")

    for placement in placements:
        f.write("\"")
        f.write(placement.id)
        f.write("\"\t\"")
        f.write(placement.job_id)
        f.write("\"\t\"")
        f.write(placement.candidate_id)
        f.write("\"\t\"")
        f.write(placement.company_id)
        f.write("\"\t\"")
        f.write(placement.company_name)
        f.write("\"\t\"")
        f.write(placement.placement_date)
        f.write("\"\t\"")
        f.write(placement.placed_by)
        f.write("\"")
        f.write("\n")

    f.close()

    validate_data = pd.read_csv(target_dir + "/placement_index_data.tsv", dtype=object, header=0,  delimiter="\t", quotechar='"' , lineterminator='\n', quoting=3, skipinitialspace=True)
    print("loaded {0} records.".format(validate_data.count()))

def write_company_drop(companies,drop_tag,drop_location):

    target_dir = drop_location + drop_tag
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    f = open(target_dir + "/company_index_data.tsv", "w")
    f.write("ID\tCompanyName\tCountry\n")

    for company in companies:
        f.write("\"")
        f.write(company.id)
        f.write("\"\t\"")
        f.write(company.company_name)
        f.write("\"\t\"")
        f.write(company.country)
        f.write("\"")
        f.write("\n")

    f.close()

    validate_data = pd.read_csv(target_dir + "/company_index_data.tsv", dtype=object, header=0,  delimiter="\n", quotechar='"' , lineterminator='\n', quoting=3, skipinitialspace=True)
    print("loaded {0} records.".format(validate_data.count()))
