import sys
import os
import time
import shutil
from datetime import datetime
from pytz import timezone

from zoho_api import sync

sys.path.append(os.path.dirname('/'.join(sys.path[0].split("/")[0:-1])))

app_root = os.path.dirname(sys.path[0])

checkpoint_time = "2017-08-28T14%3A43%3A00.72"
checkpoint_file = os.getenv('CHECKPOINT_FILE')
credential_location = os.getenv('CREDENTIAL_LOCATION')

def write_checkpoint(cpoint):
    f = open(checkpoint_file, 'w')
    f.write(cpoint)
    f.close()

def read_checkpoint():
    print(checkpoint_file)
    if os.path.exists(checkpoint_file):
        print("exists")
        f = open(checkpoint_file, 'r')
        cpoint = f.readline()
        f.close()
        return cpoint
    else:
        now_utc = datetime.now(timezone('UTC'))
        cpoint = now_utc.strftime("%Y-%m-%dT%H:%M:%S")
        write_checkpoint(cpoint)
        return cpoint

checkpoint = ""

checkpoint = read_checkpoint()

checkpoint = checkpoint.replace("\n","")

items_to_sync = ["candidates","positions","interviews","placements"]

while True:

    print("Current checkpoint is {0}".format(checkpoint))

    now_utc = datetime.now(timezone('UTC'))
    checkpoint_now = now_utc.strftime("%Y-%m-%dT%H:%M:%S")

    print ("Time is {0}".format(checkpoint))

    print(checkpoint)

    work_done, drop_tag = sync(checkpoint,items_to_sync,credential_location)

    print(work_done, drop_tag)

    if work_done:

        checkpoint = checkpoint_now

        write_checkpoint(checkpoint)

    time.sleep(60)
