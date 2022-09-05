import operator
import pprint
from collections import OrderedDict
from operator import getitem

import requests
import json

sp_lifecycle_mgt = {}
sp_lifecycle_mgt = {
    # Testcase Id
    1234: {
        # TestRuns Id
        199: {"storyId": 200, "testcaseId": 0, "testMomentStatusId": 0},
        500: {"storyId": 501, "testcaseId": 0, "testMomentStatusId": 0},
        -1: {"storyId": 0, "testcaseId": 0, "testMomentStatusId": 0}
    },
    4321: {
        611: {"storyId": 11, "testcaseId": 0, "testMomentStatusId": 0},
        -1: {"storyId": -1, "testcaseId": 0, "testMomentStatusId": 0}
    },
    999: {
        999: {"storyId": 11, "testcaseId": 0, "testMomentStatusId": 0},
        -999: {"storyId": -1, "testcaseId": 0, "testMomentStatusId": 0}
    }
}
sp_lifecycle_mgt.update({
    10: {
        # TestRuns Id
        199: {"storyId": 1990, "testcaseId": 0, "testMomentStatusId": 0},
        102423: {"storyId": 1024230, "testcaseId": 0, "testMomentStatusId": 0},
        10: {"storyId": 100, "testcaseId": 0, "testMomentStatusId": 0},
        -896: {"storyId": -8960, "testcaseId": 0, "testMomentStatusId": 0}
    }
})

# pprint.pprint(sorted(sp_lifecycle_mgt, key=operator.itemgetter(0)))
# pprint.pprint(sorted(sp_lifecycle_mgt))
# pprint.pprint(sp_lifecycle_mgt.keys())
# res = OrderedDict(sorted(sp_lifecycle_mgt.items(), key = lambda x: getitem(x[1], 'marks')))

# pprint.pprint(sp_lifecycle_mgt[10][10])
for tc_id in sp_lifecycle_mgt:
    # print( tc_id )
    print()
    pprint.pprint(sp_lifecycle_mgt[tc_id])
    tr_ids = sp_lifecycle_mgt[tc_id]
    # tr_ids = OrderedDict(sorted(tr_ids.items()))

    tc_tr_id_first = sorted(list(tr_ids))[0]
    tc_tr_id_last = sorted(list(tr_ids))[-1]
    for tr_id in tr_ids:
        pprint.pprint(tr_ids[tr_id])


exit("")
pprint.pprint(sp_lifecycle_mgt)
print()
print(sp_lifecycle_mgt)
print("keys....")
tc_tr_ids = sorted(list(sp_lifecycle_mgt.keys()))
print(tc_tr_ids)
print("first, last...")
tc_tr_id_first = tc_tr_ids[0]
tc_tr_id_last = tc_tr_ids[-1]
pprint.pprint(tc_tr_id_first)
pprint.pprint(tc_tr_id_last)
# exit("")
print("first dict...")
first = (sp_lifecycle_mgt[tc_tr_id_first])
pprint.pprint(sp_lifecycle_mgt[tc_tr_id_first])
print("last dict...")
pprint.pprint(sp_lifecycle_mgt[tc_tr_id_last])
# pprint.pprint(list(sp_lifecycle_mgt[tc_tr_id].keys())[-1])

exit("")
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

storyId = "8247"
url = "https://www16.v1host.com/api-examples/rest-1.v1/Data/Test"
title = "test T - Sat"
description = "lets do it - desc"

payload = """<?xml version="1.0" encoding="UTF-8"?>
<Asset href="/HMHealthSolutions/rest-1.v1/New/Test">
	<Attribute name="Name" act="set">""" + title + """</Attribute>
	<Attribute name="Description" act="set">""" + description + """</Attribute>
    
<!-- Newly created Story -->
    <Relation name="Parent" act="set">
       <Asset href="/HMHealthSolutions/rest-1.v1/Data/Story/""" + storyId + """" idref="Story:""" + storyId + """" />
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
