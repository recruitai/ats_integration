import sys
import os
import time
import shutil
from datetime import datetime
from pytz import timezone

from tr_api import sync

sys.path.append(os.path.dirname('/'.join(sys.path[0].split("/")[0:-1])))

app_root = os.path.dirname(sys.path[0])

checkpoint_file = os.getenv('CHECKPOINT_FILE')
credential_location = os.getenv('CREDENTIAL_LOCATION')


def write_checkpoint(cpoint):
    f = open(checkpoint_file, 'w')
    f.write(cpoint)
    f.close()

def read_checkpoint():
    if os.path.exists(checkpoint_file):
        f = open(checkpoint_file, 'r')
        cpoint = f.readline()
        f.close()
        return cpoint
    else:
        now_utc = datetime.now(timezone('UTC'))
        cpoint = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        write_checkpoint(cpoint)
        return cpoint

#loop every 5 seconds
checkpoint = ""

#read the latest checkpoint, if no checkpoint exists then one will be created
#at time now
checkpoint = read_checkpoint()

checkpoint = checkpoint.replace("\n","")

items_to_sync = ["candidates","positions"]

while True:


    print ("Current checkpoint is {0}".format(checkpoint))
    #mark the current time

    now_utc = datetime.now(timezone('UTC'))
    checkpoint_now = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    print ("Time is {0}".format(checkpoint))
    #sync to the current checkpoint

    print(checkpoint)

    work_done, drop_tag = sync(checkpoint, items_to_sync,credential_location)

    print(work_done, drop_tag)

    if work_done:

        checkpoint = checkpoint_now

        write_checkpoint(checkpoint)

    time.sleep(60)
