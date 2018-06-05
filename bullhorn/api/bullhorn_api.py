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

from BullhornREST import BullhornREST

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


def make_list_request(url,rest):

    # set max per page = 100


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
                    #print(len(jres["data"]))
                    reslist += jres["data"]
                    i+=1
                except:
                    print("failed to connect- retrying")
                #time.sleep(0.5)

        res={}
        res["Results"]=reslist
        res["TotalRecords"]=total_records

        print("total_records",len(reslist))

        return res


def sync_candidates(date_since,date_now, rest):


    field_list = "id,address,firstName,lastName,occupation,dateLastModified,dateAdded,companyName,experience,customText4,employmentPreference,educationDegree,candidateSource,source,status,desiredLocations,description"

    candidate_list_query = "search/Candidate?query=dateLastModified:[{0} TO {1}] AND isDeleted:0&sort=dateLastModified&fields={2}&count=100".format(date_since,date_now,field_list)

    url = candidate_list_query

    # set max per page = 100

    #rest_token = get_rest_token()

    jres = rest.make_rest_call(url)

    file_part_count = 0
    if "data" in jres:
        reslist = jres["data"]
        total_records = jres["total"]

        print("Total Records={0}".format(total_records))

        if total_records > 0:

            total_records = float(total_records)
            pages = 1
            if total_records > 100:

                pages = total_records / 100
                pages=int(pages)

                print("Pages={0}".format(pages))

            i=1
            k=0
            while i < pages+1:
                try:
                    start = (i*100)
                    print(url+ "&start=" + str(start))
                    jres = rest.make_rest_call(url+ "&start=" + str(start))
                    #print(len(jres["data"]))
                    reslist += jres["data"]
                    i+=1
                    k+=1
                    if k == 1:
                        k=0
                        print("saving results...")
                        save_results(reslist,file_part_count)
                        file_part_count+=1
                        reslist=[]
                except:
                   print("failed to connect- retrying")
                   time.sleep(0.5)
            return True
        else:
            return False
    else:
        return False

def save_results(jres,file_index):

    candidates=[]

    if jres != None:

        candidates_list=jres

        for cand in candidates_list:

            candidate=Candidate()
            candidate.id="c" + str(cand["id"])

            #print(candidate.id)

            if "address" in cand:
                addr = cand["address"]
                if "countryName" in addr:
                    if addr["countryName"] != None:
                        candidate.location=addr["countryName"].encode("utf-8").strip()

                if "city" in addr:
                    if addr["city"] != None:
                        candidate.city=addr["city"].encode("utf-8").strip()

                if "state" in addr:
                    if addr["state"] != None:
                        candidate.state=addr["state"].encode("utf-8").strip()

                if "zip" in addr:
                    if addr["zip"] != None:
                        candidate.postal_code=addr["zip"].encode("utf-8").strip()

            if "firstName" in cand:
                if cand["firstName"] != None:
                    candidate.first_name=cand["firstName"].encode("utf-8").strip()

            if "lastName" in cand:
                if cand["lastName"] != None:
                    candidate.last_name=cand["lastName"].encode("utf-8").strip()

            if "occupation" in cand:
                if cand["occupation"] != None:
                    candidate.job_title=cand["occupation"].encode("utf-8").strip()

            if "status" in cand:
                if cand["status"] != None:
                    candidate.status=cand["status"].encode("utf-8").strip()

            if "source" in cand:
                if cand["source"] != None:
                    if len(cand["source"]) > 0:
                        candidate.candidate_source=cand["source"][0].encode("utf-8").strip()

            if "customText4" in cand:
                if cand["customText4"] != None:
                    candidate.notice_period=cand["customText4"].encode("utf-8").strip()

            if "employmentPreference" in cand:
                if cand["employmentPreference"] != None:
                    if len(cand["employmentPreference"]) > 0:
                        candidate.employment_preference=cand["employmentPreference"][0].encode("utf-8").strip()

            if "experience" in cand:
                if cand["experience"] != None:
                    candidate.experience=str(cand["experience"])

            if "dateAdded" in cand:
                if cand["dateAdded"] != None:
                    date_added = datetime.fromtimestamp(int(cand["dateAdded"])/1000).strftime('%Y-%m-%dT%H:%M:%S')
                    candidate.date_entered=date_added

            if "dateLastModified" in cand:
                if cand["dateLastModified"] != None:
                    date_last_modified = datetime.fromtimestamp(int(cand["dateLastModified"])/1000).strftime('%Y-%m-%dT%H:%M:%S')
                    candidate.last_modified=date_last_modified

            if "description" in cand:
                if cand["description"] != None:

                    #print("description",cand["description"])
                    parsed = strip_tags(cand["description"].encode("utf-8"))

                    if len(parsed) == 0:
                        parsed = cand["description"]

                    #temp fix until do a full rebuild of bullhorn sandbox
                    # parsed = re.sub(r'^https?:\/\/.*[\r\n]*', '', parsed, flags=re.MULTILINE)
                    # parsed = re.sub(r'^----boundary.*', '', parsed, flags=re.MULTILINE)
                    # parsed = re.sub(r'=[A-F][0-9]',r'', parsed)
                    # parsed = re.sub(r'=[0-9][A-F]',r'', parsed)
                    # parsed = re.sub(r'=[A-F][A-F]',r'', parsed)
                    # parsed = re.sub(r'=',r'', parsed)
                    # parsed = re.sub(r'o=',r'', parsed)

                    candidate.resume_words=cleanup_text(parsed)

            if "companyName" in cand:
                if cand["companyName"] != None:
                    candidate.current_company=cand["companyName"].encode("utf-8").strip()

            candidates.append(candidate)

        if len(candidates) > 0:
            write_candidate_data(candidates)

def sync_positions(date_since,date_now,countryLookup,rest):

    field_list = "id,externalID,address,title,status,clientCorporation,dateLastModified,dateAdded,description,isOpen"

    position_list_query = "search/JobOrder?query=dateLastModified:[{0} TO {1}] AND isDeleted:0&sort=dateLastModified&fields={2}&count=100".format(date_since,date_now,field_list)

    url = position_list_query

    print(url)

    jres = make_list_request(url,rest)

    positions=[]
    if jres != None:

        position_list=jres["Results"]
        total_records=jres["TotalRecords"]

        for pos in position_list:

            #print(pos)

            position=Position()
            position.id="p" + str(pos["id"])

            if "title" in pos:
                if pos["title"] != None:
                    position.job_title=pos["title"].encode("utf-8").strip()

            if "address" in pos:
                addr = pos["address"]
                if "countryID" in addr:
                    if addr["countryID"] != None:
                        position.position_location=countryLookup[addr["countryID"]].encode("utf-8")

                if "city" in addr:
                    if addr["city"] != None:
                        position.city=addr["city"].encode("utf-8").strip()

                if "state" in addr:
                    if addr["state"] != None:
                        position.state=addr["state"].encode("utf-8").strip()

                if "zip" in addr:
                    if addr["zip"] != None:
                        position.postal_code=addr["zip"].encode("utf-8").strip()

            if "clientCorporation" in pos:
                company = pos["clientCorporation"]
                if "name" in company:
                    if company["name"] != None:
                        position.company_name=company["name"].encode("utf-8").strip()

            if "externalID" in pos:
                if pos["externalID"] != None:
                    position.position_id=pos["externalID"].encode("utf-8").strip()

            if "status" in pos:
                if pos["status"] != None:
                    position.status=pos["status"].encode("utf-8").strip()

            if "isOpen" in pos:
                if pos["isOpen"] != None:
                    if pos["isOpen"] == True:
                        position.open_closed="Open"
                    else:
                        position.open_closed="Closed"

            if "dateAdded" in pos:
                if pos["dateAdded"] != None:
                    date_added = datetime.fromtimestamp(int(pos["dateAdded"])/1000).strftime('%Y-%m-%dT%H:%M:%S')
                    position.date_entered=date_added

            if "dateLastModified" in pos:
                if pos["dateLastModified"] != None:
                    date_last_modified = datetime.fromtimestamp(int(pos["dateLastModified"])/1000).strftime('%Y-%m-%dT%H:%M:%S')
                    position.last_modified=date_last_modified

            if "description" in pos:
                if pos["description"] != None:
                    position.job_description_words=cleanup_text(pos["description"].encode("utf-8"))

            positions.append(position)

    return positions

def sync(checkpoint_time,items_to_sync,credential_location):

    #rest_token = get_rest_token()
    credential_location = os.getenv('CREDENTIAL_LOCATION')

    rest = BullhornREST(credential_location)
    rest.update_rest_token()

    countries = rest.make_rest_call("options/Country?count=300&")

    countryLookup = {}
    for cnt in countries["data"]:
        #print (cnt["value"],cnt["label"])
        countryLookup[cnt["value"]] = cnt["label"].lower()

    dcheck = datetime.strptime(checkpoint_time, '%Y-%m-%dT%H:%M:%S')
    date_since = dcheck.strftime('%Y%m%d%H%M%S')

    now_utc = datetime.now(timezone('UTC'))
    date_now = now_utc.strftime('%Y%m%d%H%M%S')

    has_work = False

    if "candidates" in items_to_sync:
        has_work = sync_candidates(date_since,date_now,rest)

    if "positions" in items_to_sync:
        positions = sync_positions(date_since,date_now,countryLookup,rest)

        if len(positions) > 0:
            has_work=True

    if has_work:

        if "positions" in items_to_sync:
            write_position_data(positions)
            print ("updated {0} position records.".format(len(positions)))

        return (True, "")
    else:
        return(False, "")


if __name__ == '__main__':

    checkpoint_time = "2018-03-12T16:50:00"
    items_to_sync = ["candidates"]
    credential_location = "../"

    sync(checkpoint_time,items_to_sync,credential_location)
