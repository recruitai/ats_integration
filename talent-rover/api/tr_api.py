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

from bs4 import BeautifulSoup


from TalentRoverREST import TalentRoverREST

sys.path.append(os.path.dirname('/'.join(sys.path[0].split("/")[0:-1])))

printable = set(string.printable)

from utilities.document_to_text import document_to_text_bin


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
    s.feed(html.decode("utf-8"))
    return s.get_data()

def strip_html_bs(data):
    soup = BeautifulSoup(data,"lxml")
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text = soup.get_text()
    return text

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


def sync_candidates(date_since,date_now, rest):


    #salesforce is limited to 2000 records returned but will return the total number of rows
    #we iterate through 2000 at a time updating the query criteria with the LastModifiedDate of
    #the last processed record

    keep_processing = True
    work_done = False

    while keep_processing:

        print(date_since)
        results = rest.make_rest_call("query?q=SELECT+Id,Name,LastName,FirstName,Title,LastModifiedDate,CreatedDate,OtherCountry+FROM+Contact+WHERE+LastModifiedDate+>+{0}+ORDER+BY+LastModifiedDate+asc".format(date_since)) #+LIMIT+20

        result_rows = len(results["records"])

        if result_rows > 0:
            total_result_rows  = results["totalSize"]

            print(results["totalSize"],len(results["records"]))

            stage_results(results["records"],rest)

            work_done = True
            if total_result_rows > 2000:
                date_since = results["records"][-1]["LastModifiedDate"].replace(".000+0000","Z")
            else:
                keep_processing = False
        else:
            keep_processing = False

    #return last updated checkpoint
    return work_done


def stage_results(results, rest):

    #break down the, potentially 2000 updates into 100*20 chunks
    results_to_save = []
    i=0
    for res in results:
        results_to_save.append(res)
        i+=1
        if i == 100:
            save_results(results_to_save,rest)
            i=0
            results_to_save=[]
    if i > 0:
        save_results(results_to_save,rest)


    #iterate results and save to rai

def save_results(jres,rest):

    #map the data to fields expected in Recruit AI and save
    candidates=[]
    if jres != None:

        candidates_list=jres

        for cand in candidates_list:

            candidate=Candidate()
            candidate.id="c" + str(cand["Id"])

            #print(candidate.id)
            if "OtherCountry" in cand:
                if cand["OtherCountry"] != None:
                    candidate.location=cand["OtherCountry"].encode("utf-8").strip()

            if "FirstName" in cand:
                if cand["FirstName"] != None:
                    candidate.first_name=cand["FirstName"].encode("utf-8").strip()

            if "LastName" in cand:
                if cand["LastName"] != None:
                    candidate.last_name=cand["LastName"].encode("utf-8").strip()

            if "Title" in cand:
                if cand["Title"] != None:
                    candidate.job_title=cand["Title"].encode("utf-8").strip()

            if "CreatedDate" in cand:
                if cand["CreatedDate"] != None:
                    date_added = cand["CreatedDate"]
                    candidate.date_entered=date_added

            if "LastModifiedDate" in cand:
                if cand["LastModifiedDate"] != None:
                    date_last_modified = cand["LastModifiedDate"]
                    candidate.last_modified=date_last_modified

            #get the resume text
            resume_text = get_resume(cand["Id"],rest)

            if resume_text is not None:
                #clean up the resume text and split into words
                candidate.resume_words=cleanup_text(resume_text)
                candidates.append(candidate)


        if len(candidates) > 0:
            write_candidate_data(candidates)


    return

def get_resume(candidate_id, rest):

    #resumes are mapped via ContactDocument entities
    results = rest.make_rest_call("query?q=SELECT+Id,+Name,+TR1__Contact__c+,+TR1__Internal_URL__c,+LastModifiedDate,TR1__Version__c+FROM+TR1__ContactDocument__c+WHERE+TR1__Contact__c+=+'{0}'+AND+TR1__Type__c+=+'Resume'".format(candidate_id))

    #get the latest version of the resume
    results = results["records"]
    if len(results) > 0:
        imax = 0
        mv = 0
        i=0
        for resume in results:
            if resume["TR1__Version__c"] > mv:
                mv = resume["TR1__Version__c"]
                imax = i
            i+=1

        #TO DO: add full .doc and .rtf suport
        resume = results[imax]
        filename = resume["Name"]
        fext = ".pdf"
        if len(filename) > 5:
            if filename[-5:].lower() == ".docx":
                fext = ".docx"
        if len(filename) > 4:
            if filename[-4:].lower() == ".doc":
                fext = ".doc"
            if filename[-4:].lower() == ".rtf":
                fext = ".rtf"

        #no clean way to resolve the attachment ID so parse the URL link
        download_link = resume["TR1__Internal_URL__c"]
        index_of_id = download_link.find("file=")
        index_of_slash = download_link.find("\"",index_of_id)
        attachment_id = download_link[index_of_id+5:]
        #make call for the raw attachment
        body = rest.make_rest_call_raw("sobjects/Attachment/{0}/Body".format(attachment_id))

        #call the relevant parsing engine to extract the text
        resume_text = document_to_text_bin(body,fext,filename)

        return resume_text



def sync_positions(date_since,date_now,rest):

    #salesforce is limited to 2000 records returned but will return the total number of rows
    #we iterate through 2000 at a time updating the query criteria with the LastModifiedDate of
    #the last processed record
    keep_processing = True
    work_done = False

    while keep_processing:

        results = rest.make_rest_call("query?q=SELECT+Id,Name,TR1__Account_Name__c,TR1__City__c,TR1__Client_Job_Description__c,LastModifiedDate,CreatedDate+FROM+TR1__Job__c+WHERE+LastModifiedDate+>+{0}+ORDER+BY+LastModifiedDate+asc".format(date_since))

        result_rows = len(results["records"])

        if result_rows > 0:

            total_result_rows  = results["totalSize"]

            print(results["totalSize"],len(results["records"]))

            positions = []

            for pos in results["records"]:

                position=Position()
                position.id="p" + str(pos["Id"])

                if "Name" in pos:
                    if pos["Name"] != None:
                        position.job_title=pos["Name"].encode("utf-8").strip()

                if "TR1__Account_Name__c" in pos:
                    if pos["TR1__Account_Name__c"] != None:
                        position.company_name=pos["TR1__Account_Name__c"].encode("utf-8").strip()

                if "TR1__City__c" in pos:
                    if pos["TR1__City__c"] != None:
                        position.position_location=pos["TR1__City__c"].encode("utf-8").strip()

                if "TR1__Client_Job_Description__c" in pos:
                    if pos["TR1__Client_Job_Description__c"] != None:
                        position.description=cleanup_text(strip_html_bs(pos["TR1__Client_Job_Description__c"].encode("utf-8").strip()))

                if "CreatedDate" in pos:
                    if pos["CreatedDate"] != None:
                        date_added = pos["CreatedDate"]
                        position.date_entered=date_added

                if "LastModifiedDate" in pos:
                    if pos["LastModifiedDate"] != None:
                        date_last_modified = pos["LastModifiedDate"]
                        position.last_modified=date_last_modified

                positions.append(position)

            write_position_data(positions)

            work_done = True
            if total_result_rows > 2000:
                date_since = results["records"][-1]["LastModifiedDate"].replace(".000+0000","Z")
            else:
                keep_processing = False
        else:
            keep_processing = False

    return work_done



def sync(checkpoint_time,items_to_sync,credential_location):


    rest = TalentRoverREST(credential_location)

    rest.update_rest_token()

    print(checkpoint_time)

    dcheck = datetime.strptime(checkpoint_time, '%Y-%m-%dT%H:%M:%SZ')
    date_since = dcheck.strftime('%Y-%m-%dT%H:%M:%SZ')

    now_utc = datetime.now(timezone('UTC'))
    date_now = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    has_work = False

    if "candidates" in items_to_sync:
        has_work = sync_candidates(date_since,date_now,rest)

    if "positions" in items_to_sync:
        has_work_pos = sync_positions(date_since,date_now,rest)

        if has_work_pos:
            has_work=True

    if has_work:
        return (True, "")
    else:
        return(False, "")
