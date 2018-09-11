####TO DO####
#checkpoint_time
#add all the field_list
import sys
import os
from interfaces import Candidate
from interfaces import Position

from interfaces import write_candidate_data
from interfaces import write_position_data

import requests
import time
import base64
import StringIO

import string

import re

import json
import time

from datetime import datetime
from pytz import timezone

from zohoREST import ZohoREST

import csv

csv.field_size_limit(sys.maxsize)

printable = set(string.printable)

app_root = os.path.dirname(sys.path[0])

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

def cleanup_text(text):

    lines = text.split("\n")
    clean_lines = []
    for line in lines:
        line_text = ''
        line_text += ''.join([i if ord(i) > 31 and ord(i)
                                < 128 else ' ' for i in line])
        line_text = line_text.strip()
        line_text = ' '.join(line_text.split())
        if len(line_text) > 1:
            clean_lines.append(line_text)

    final_text = ""
    for line in clean_lines:
        final_text += line + "|"

    for x in final_text:
        if x not in printable:
            final_text = final_text.replace(x, " ")

    p = re.compile("([a-z])([A-Z])")

    pit = p.finditer(final_text)
    i = 1
    for match in pit:
        ipit = match.span()[0]
        final_text = final_text[:ipit + i] + " " + final_text[ipit + i:]
        i += 1

    return final_text

def make_list_request(url,rest):#need to pass model

    jres = rest.make_rest_call(url)
    print(jres)
    if "data" in jres:
        reslist = jres["data"]
        total_records = jres["total"]

        print("Total Records={0}".format(total_records))

        total_records = float(total_records)

        if total_records > 100:

            pages = total_records / 100
            pages=int(pages)

            print("Pages={0}".format(pages))

            i=1
            while i < pages+1:
                try:
                    start = (i*100)
                    print(url+ "&start=" + str(start))
                    jres = rest.make_rest_call(url+ "&start=" + str(start))
                    reslist += jres["data"]
                    i+=1
                except:
                    print("failed trying to connect")
        res={}
        res["Results"]=reslist
        res["TotalRecords"]=total_records

        print("total_records",len(reslist))

        return res

def sync_candidates(rest):

    field_list = "First Name,Last Name,Email,Mobile,Street,City,State,Zip Code,Country,Experience in Years,Current Employer,Current Job Title,Skill Set,Expected Salary,Current Salary,Additional Info,Created By,Created Time,Updated On,Salutation,Last Activity,Candidate Owner,Source,Email Opt Out,Is Locked,Unqualified,Attachment Present,Candidate Status"
    #below add query for dates
    candidate_list_query = "recruit/private/json/Candidates/getRecords?&version=2&newFormat=1&selectColumns=Candidates({0})&".format(field_list)

    url = candidate_list_query

    jres = rest.make_rest_call(url)
    print(jres)

    #file_part_count = 0
    if "Candidates" in jres:#make this cleaner
        print("stuff works")
        reslist = jres["Candidates"]["row"][0]["FL"]#[0]["FL"]

        print("saving results...")
        save_results(reslist)#figure out how this works
        #file_part_count+=1
        #reslist=[]
    else:
        print("something went wrong")
        return False

def save_results(jres):#add all the other fields later

    candidates = []

    if jres != None:

        candidate_list=jres

        for cand in candidate_list:

            candidate=Candidate()
            print("-------------------------------------------------------------------")
            print(cand["val"])

            if "CANDIDATEID" in cand["val"]:
                candidate.id="c" + str(cand["content"])
                print(candidate.id)

            if "First Name" in cand["val"]:
                if cand["content"] != None:
                    candidate.first_name=cand["content"].encode("utf-8").strip()

            if "Last Name" in cand["val"]:
                if cand["content"] != None:
                    candidate.last_name=cand["content"].encode("utf-8").strip()

            if "Email" in cand["val"]:
                if cand["content"] != None:
                    candidate.email = cand["content"].encode("utf-8").strip()

            if "Mobile" in cand["val"]:
                if cand["content"] != None:
                    candidate.mobile = cand["content"].encode("utf-8").strip()

            #Add location here later

            if "Street" in cand["val"]:
                if cand["content"] != None:
                    candidate.street = cand["content"].encode("utf-8").strip()

            if "City" in cand["val"]:
                if cand["content"] != None:
                    candidate.city = cand["content"].encode("utf-8").strip()

            if "State" in cand["val"]:
                if cand["content"] != None:
                    candidate.state = cand["content"].encode("utf-8").strip()

            if "Zip Code" in cand["val"]:
                if cand["content"] != None:
                    candidate.zip_code = cand["content"].encode("utf-8").strip()

            if "Experience in Years" in cand["val"]:
                if cand["content"] != None:
                    candidate.experience = cand["content"].encode("utf-8").strip()

            if "Current Employer" in cand["val"]:
                if cand["content"] != None:
                    candidate.current_employer = cand["content"].encode("utf-8").strip()

            if "Current Job Title" in cand["val"]:
                if cand["content"] != None:
                    candidate.current_job = cand["content"].encode("utf-8").strip()

            if "Additional Info" in cand["val"]:#resume words
                if cand["content"] != None:

                    parsed = strip_tags(cand["content"].encode("utf-8"))

                    if len(parsed) == 0:
                        parsed = cand["content"]

                    candidate.additional_info = cleanup_text(parsed)

            if "Created By" in cand["val"]:
                if cand["content"] != None:
                    candidate.created_by = cand["content"].encode("utf-8").strip()

            if "Created Time" in cand["val"]:
                if cand["content"] != None:
                    candidate.created_time = cand["content"].encode("utf-8").strip()

            if "Updated On" in cand["val"]:
                if cand["content"] != None:
                    candidate.updated_on = cand["content"].encode("utf-8").strip()

            if "Salutation" in cand["val"]:
                if cand["content"] != None:
                    candidate.salutation = cand["content"].encode("utf-8").strip()

            #if "Candidate Owner" in cand["val"]:
            #    if cand["content"] != None:
            #        candidate.cand_owner = candidate["content"].encode("utf-8").strip()

            #if "Source" in cand["val"]:
            #    if cand["content"] != None:
            #        candidate.source = candidate["content"].encode("utf-8").strip()

            if "Email Opt Out" in cand["val"]:
                if cand["content"] != None:
                    candidate.email_opt_out = cand["content"].encode("utf-8").strip()

            if "Is Locked" in cand["val"]:
                if cand["content"] != None:
                    candidate.is_locked = cand["content"].encode("utf-8").strip()

            if "Unqualified" in cand["val"]:
                if cand["content"] != None:
                    candidate.unqualified = cand["content"].encode("utf-8").strip()

            if "Attachment Present" in cand["val"]:
                if cand["content"] != None:
                    candidate.attachment = cand["content"].encode("utf-8").strip()

            if "Candidate Status" in cand["val"]:
                if cand["content"] != None:
                    candidate.status = cand["content"].encode("utf-8").strip()

            candidates.append(candidate)

        if len(candidates) > 0:
            write_candidate_data(candidates)

def sync_positions(rest):

    field_list = "Posting Title"

    position_list_query = "recruit/private/json/JobOpenings/getRecords?&version=2&newFormat=1&selectColumns=JobOpenings({0})".format(field_list)

    url = position_list_query

    print(url)

    jres = make_list_request(url,rest)

    positions=[]
    if jres != None:

        position_list=jres["JobOpenings"]
        #total_records=jres["TotalRecords"]

        for pos in position_list:#naming

            position=Position()
            position.id="p" + str(pos["JOBOPENINGID"])#??

            if "Posting Title" in pos:
                if pos["Posting Title"] != None:
                    position.job_title=pos["Posting Title"].encode("utf-8").strip()

            positions.append(position)

        return positions


def sync(checkpoint_time,items_to_sync,credential_location):

    credential_location = os.getenv('CREDENTIAL_LOCATION')
    print credential_location

    rest = ZohoREST(credential_location)
    rest.update_rest_token() #only update rest token if error with rest token so test it first

        #include the country lookup

        #dcheck = datetime.strptime(checkpoint_file, '%y-%m-%dT%H:%M:%S')
        #date_since = dcheck.strftime('%Ym%d%H%M%S')

        #now_utc = datetime.now(timezone('UTC'))
        #date_now = now_utc.strftime('%Y%m%d%H%M%S')

    has_work = False

    if "candidates" in items_to_sync:
        has_work = sync_candidates(rest)#add the checkpoint later

    if "positions" in items_to_sync:
        positions = sync_positions(rest)#standarize time based on country

        if len(positions) > 0:
            has_work = True

    if has_work:

        if "positions" in items_to_sync:
            write_position_data(positions)
            print ("updated {0} position records.".format(len(positions)))

        return (True, "")
    else:
        return (False, "")

if __name__ == '__main__':

    checkpoint_time = "2018-03-12T16:50:00"
    items_to_sync = ["candidates"]#add positions
    credential_location = "../"

    sync(checkpoint_time,items_to_sync,credential_location)
