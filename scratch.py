import requests
import json

url = "https://highmarkhealth.spiraservice.net/services/v6_0/RestService.svc/projects?username=anthony.ennis@hmhs.com&api-key={CF69015D-5208-4848-9E42-51CE9FA9CD7B}"

payload = {}
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

# exit("x")

import requests

url = "https://www16.v1host.com/api-examples/rest-1.v1/Hist/Story?sel=Name,ToDo,ChangeDate"

payload = {}
headers = {
    'Authorization': 'Bearer 1.VvzUpAo8PbdPEcbb2ol96VpcvfI=',
    'Accept': 'application/json'
}

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)


import yaml

with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

for section in cfg:
    print(section)
print(cfg["spira"])
print(cfg["digital"])
print(type(cfg["mocks"]))
print(cfg["mocks"]["spira"]["project"])
projIds = cfg["mocks"]["spira"]["project"]
for projId in projIds:
    print(projId)

sp_lifecycle_mgt = {
    0: {
        "storyId": 0,
        "testcaseId": 0,
        "testMomentStatusId": 0
    }
}

sp_lifecycle_mgt[0]["storyId"] = 0
sp_lifecycle_mgt[0]["testcaseId"] = 0
sp_lifecycle_mgt[0]["testMomentStatusId"] = 0
print("\n", sp_lifecycle_mgt)

sp_lifecycle_mgt[0]["storyId"] = 0
sp_lifecycle_mgt[0]["testcaseId"] = 0
sp_lifecycle_mgt[0]["testMomentStatusId"] += 1
print("\n", sp_lifecycle_mgt)

storyId="8247"
url = "https://www16.v1host.com/api-examples/rest-1.v1/Data/Test"
title="test T - Sat"
description="lets do it - desc"

payload = """<?xml version="1.0" encoding="UTF-8"?>
<Asset href="/HMHealthSolutions/rest-1.v1/New/Test">
	<Attribute name="Name" act="set">"""+title+"""</Attribute>
	<Attribute name="Description" act="set">"""+description+"""</Attribute>
    
<!-- Newly created Story -->
    <Relation name="Parent" act="set">
       <Asset href="/HMHealthSolutions/rest-1.v1/Data/Story/"""+storyId+"""" idref="Story:"""+storyId+"""" />
    </Relation>
</Asset>
"""
headers = {
    'Authorization': 'Bearer 1.VvzUpAo8PbdPEcbb2ol96VpcvfI=',
    'Accept': 'application/json',
    'Content-Type': 'application/xml'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
result = response.json()
testcaseId = result["id"].split(":")[1]
testcaseMomentId = result["id"].split(":")[2]
storyId = result["Attributes"]["Parent"]["value"]["idref"].split(":")[1]
print("INF: ai_storyId: ", storyId)
print("INF: ai_testcaseId: ", testcaseId)
print("INF: ai_testcaseMomentId: ", testcaseMomentId)
