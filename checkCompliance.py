import time
from cvprac.cvp_client import CvpClient ## CVPRAC, in pip.
import urllib3
import json
import requests
import socket
import csv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #ignores ssl-cert validation.

##### Requires special fork of CVPRAC currently - waiting on PR to be merged in main repo.
### https://github.com/brokenpackets/cvprac
####User Data
cvp_url = '1.2.3.4'
cvp_user = 'cvpadmin'
cvp_pass = 'arista'
slack_url = 'https://hooks.slack.com/services/slack/incoming/webhook/config'
slack_user = socket.gethostname()
####

clnt = CvpClient() #Create CVPClient session.

clnt.connect([cvp_url], cvp_user, cvp_pass,protocol='https') #Create connection to CVP IP, with creds in-line.
cntr_bundle = clnt.api.get_devices_in_container("Undefined") # get list of devices in container "Undefined"

#########Functions#########
def rewrite_csv():
    with open('lastlog.csv','w+') as fw:
        wr = csv.writer(fw)
        rowvalue = loglist
        wr.writerows(rowvalue)

def write_csv(fqdn,timestamp):
    with open('lastlog.csv','a+') as fw:
        wr = csv.writer(fw)
        rowvalue = (fqdn, str(timestamp))
        wr.writerow(rowvalue)
def webhook(slack_data):
    payload = {
    'username': slack_user,
    'text': slack_data
    }

    response = requests.post(
        slack_url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

def check_Compliance():
    eventID = clnt.api.check_compliance('root', 'container')['data']
    eventStatus = True
    while eventStatus:
        time.sleep(5)
        querystatus = clnt.api.get_EventDatabyId(eventID)
        if all([item['status'] == 'COMPLETED' for item in querystatus]):
            eventStatus = False

def get_Inventory():
    inventory = clnt.api.get_inventory()
    out_of_compliance = []
    devicelist = []
    print 'Posting Devices to Slack'
    for item in inventory:
        if item['complianceIndication'] == 'WARNING':
            out_of_compliance = item['fqdn']
            if out_of_compliance:
                if out_of_compliance not in str(loglist):
                    slack_data = 'Device out of compliance:\n'+out_of_compliance
                    print slack_data
                    webhook(slack_data)
                    write_csv(out_of_compliance,int(time.time()))


def create_Snapshot():
    snapshot = clnt.api.capture_ContainerLevelSnapshot('Initial_Template', 'root')
##########################

####CSV Manipulation:
## Step 1: If lastlog.csv exists, mount contents as loglist
## Step 2: Remove any items from loglist > 1 day old.
## Step 3: Rewrite CSV File without removed lines.
try:
  with open('lastlog.csv', 'rb') as f:
      reader = csv.reader(f)
      loglist = list(reader)
      loglist2 = list(loglist)
      for items in loglist2:
          if int(items[1]) + 86400 < int(time.time()):
              loglist.remove(items) #remove items with timestamp older than 1 day in seconds.
              rewrite_csv()
####Just in case this is a first-time run, builds lastlog.csv and proceeds.
except:
  with open('lastlog.csv', 'a+') as f:
      reader = csv.reader(f)
      loglist = list(reader)


####Actions
print 'Creating Snapshot of devices'
create_Snapshot()
print '######'
print 'Snapshot Created'
print '######'
print 'Checking device Compliance'
check_Compliance()
print '######'
print 'Device Compliance Check Complete'
print '######'
print 'Checking devices for compliance status'
get_Inventory()
print '######'
print 'Writing out-of-compliance devices to file'

print 'Complete.'
