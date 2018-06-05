# Setting up and Configuring a Bullhorn API Component

## Introduction

This guide will describe how to set up and configure a Bullhorn API Component for Recruit AI. The API Component is in the form of a set of python scripts, which when running will request data from the Bullhorn REST API and upload it to the Recruit AI API.

The API integration component works as follows

1. Authenticate with the Bullhorn REST API
2. Manage a checkpoint- a date/time when data was last requested from the ATS
3. Request Candidate and Position data from the ATS that has been modified since the last checkpoint
4. Parse the data into the correct format to feed to Recruit AI
5. Authenticate with the Recruit AI REST API
6. Post the data to the /public/candidate and /public/position routes

The component can run anywhere, in this guide we will list the steps to run on an AWS instance.

## Steps

#### Step 1. Create an Ubuntu 16.04 AWS instance to run the component.

```
Micro-instance
No EBS Volumes required
Open port 22
```

#### Step 2. Install the following components
```
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install python-pip
sudo apt-get install python-dev
sudo pip install requests
sudo apt-get install python-m2crypto
sudo pip install pytz
```

Install node.js and npm (this is for using pm2 process control manager later on)
```
curl -sL https://deb.nodesource.com/setup_8.x -o 
nodesource_setup.sh
sudo apt-get install nodejs
npm install pm2@latest -g
pm2 install pm2-logrotate
```


#### Step 3. Clone the API component from github
```
git clone https://github.com/recruitai/ats_integration
```
#### Step 4. Set up environment variables

Get your API URL and API key for Recruit AI

Create env.bash in the home directory and add the following lines to the file substituting url for the url of the Recruit AI instance and 123456 with your Recruit AI API key.

```
export RECRUIT_AI_URL=url
export RECRUIT_AI_KEY=123456
export CHECKPOINT_FILE=/home/ubuntu/checkpoint.txt
export CREDENTIAL_LOCATION=/home/ubuntu/

source ~/env.bash
```
#### Step 5. Initialize Credentials

```
cd ats_integration/bullhorn/api
```

Get your API login details for Bullhorn and run the bullhorn_initialize.py script with the following parameters (ensure you escape the password correctly)

```
python bullhorn_initialize.py username password client_id client_secret 
```

#### Step 6. Verify the Script runs correctly

```
python sync_api_bh.py
```

#### Step 7.  Setup pm2

```
pm2 start sync_api_bh.py --name bullhorn_api_sync
pm2 save
```

Check all is ok by running:
```
pm2 logs
```
