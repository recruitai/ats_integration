import os
import sys
import subprocess
import re
import time
import shutil

def convert_rtf_to_pdf(target_file,target_dir):

    print(target_file)
    print(target_dir)
    subprocess.call( ['soffice',
                     '--invisible',
                     '--headless',
                     '--convert-to',
                     'pdf',
                     target_file,
                     '--outdir',
                     target_dir] )


def convert_candidate_resumes(candidates,drop_location):

    for candidate in candidates:
        convert_rtf_to_pdf(drop_location + "resumes/" + candidate.id + ".rtf",drop_location + "converted/")

if __name__ == '__main__':

    drop_data_path = os.getenv('DROP_DATA')

    target_dir = "/data/resumes/"
    target_file_dir = drop_data_path + "/resume_queue/"
    archive_file_dir = drop_data_path + "/resume_queue_archive/"

    while True:
        print("waiting...")
        for src_file in os.listdir(target_file_dir):
            if src_file.endswith(".pdf") == True:
                shutil.move(target_file_dir + src_file, target_dir + src_file)
                print("moved .pdf file {0}".format(src_file))
            else:
                print("processing {0} ...".format(src_file))
                convert_rtf_to_pdf(target_file_dir + src_file,target_dir)
                shutil.move(target_file_dir + src_file, archive_file_dir + src_file)
            print("processed {0} ...".format(src_file))

        time.sleep(20)
