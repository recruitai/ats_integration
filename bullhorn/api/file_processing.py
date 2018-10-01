import base64
import os
import sys
import time

from BullhornREST import BullhornREST

sys.path.append(os.path.dirname('/'.join(sys.path[0].split("/")[0:-1])))

from utilities.document_to_text import document_to_text

def get_candidate_resume_text(candidate_id,rest):

    url = "entityFiles/Candidate/{0}?".format(candidate_id)

    file_url = "file/Candidate/{0}/{1}?"

    print(url)

    jres = rest.make_rest_call(url)

    print(jres)

    entity_files = jres["EntityFiles"]
    text = ""
    if len(entity_files) > 0:

        latest_resume_file = ""
        latest_resume_ext = ""

        for ef in entity_files:
            if ef["type"] == "CV":
                latest_resume_file = ef["id"]
                latest_resume_ext = ef["fileExtension"]

        print(latest_resume_file)

        try:
            latest_resume_data = rest.make_rest_call(file_url.format(candidate_id,latest_resume_file))
            #print(latest_resume_data)

            content = latest_resume_data["File"]["fileContent"]
            file_name = latest_resume_data["File"]["name"]
            print(latest_resume_ext)
            print(file_name)
            text = document_to_text(content, latest_resume_ext, file_name)
        except Exception as ex:
            print(ex)
        return text


def get_file_candidates(rest):

    field_list = "id,description"

    candidate_list_query = "search/Candidate?query=isDeleted:0&sort=dateLastModified&fields={0}&count=100".format(field_list)

    url = candidate_list_query

    # set max per page = 100

    #rest_token = get_rest_token()

    jres = rest.make_rest_call(url)

    file_part_count = 0
    if "data" in jres:
        reslist = []
        total_records = jres["total"]

        print("Total Records={0}".format(total_records))

        if total_records > 0:

            total_records = float(total_records)
            pages = 1
            if total_records > 100:

                pages = total_records / 100
                pages=int(pages)

                print("Pages={0}".format(pages))

            i=600
            k=0
            while i < pages+1:
                try:
                    start = (i*100)
                    print(url+ "&start=" + str(start))
                    jres = rest.make_rest_call(url+ "&start=" + str(start))
                    print(len(jres["data"]))
                    reslist += jres["data"]
                    i+=1
                    k+=1
                    if k == 1:
                        k=0
                        candidates_list=reslist
                        for cand in candidates_list:
                            if cand["description"] == "":
                                print(cand["id"])
                                print(get_candidate_resume_text(cand["id"],rest))
                        file_part_count+=1
                        reslist=[]
                except Exception as ex:
                  print(ex)
                  print("failed to connect- retrying")
                  time.sleep(0.5)
            return True
        else:
            return False
    else:
        return False


if __name__ == '__main__':

    credential_location = os.getenv('CREDENTIAL_LOCATION')

    rest = BullhornREST(credential_location)
    rest.update_rest_token()
    #test
    get_file_candidates(rest)
