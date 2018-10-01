# Talent Rover API Component

## Introduction

The API Component is in the form of a set of python scripts, which when running will request data from the Talent Rover Salesforce REST API and upload it to the Recruit AI API.

The API integration component works as follows

1. Authenticate with the Sales Force REST API
2. Manage a checkpoint- a date/time when data was last requested from the ATS
3. Request Candidate and Position data from the ATS that has been modified since the last checkpoint
4. Parse the data into the correct format to feed to Recruit AI
5. Authenticate with the Recruit AI REST API
6. Post the data to the /public/candidate and /public/position routes


## Background

Talent Rover runs on the Salesforce platform and so integration is via the Salesforce API. Salesforce provide a standard REST API and a BULK API.

This repo uses the standard REST API. Salesforce enforces atrict API limits at 15,000 calls per day, so any call for data or indeed the limits themselves will count towards this limit.

The API is not sandboxed from the Talent Rover application so if the API limits are hit the main application will stop functioning.

With this is mind, the API components monitor the API limits while syncing and stops when a specified threshold is met.

## Configuration

Configuration is via two environment variables and a .json credential file.

* CHECKPOINT_FILE - the full path to a file to store the current checkpoint
* CREDENTIAL_LOCATION - the directory of credentials.json

credentials.json

```
{"instance_url":"https://xxx.salesforce.com/","username": "YOUR_USERNAME", "client_secret": "YOUR_CLIENT_SECRET", "password": "YOUR_PASSWORD+ACCESS_TOKEN", "client_id": "CLIENT_ID"}
```
