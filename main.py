import operator
import pprint
from collections import OrderedDict
from datetime import datetime

import requests
import yaml

# Globals
ai_test_storyId = "8247"
ai_test_title = ""
ai_test_description = ""
ai_test_status = ""
ai_test_owners = ""

sp_project_data = []
sp_project_req_data = []
sp_project_testcase_data = []
sp_project_teststep_data = []
sp_project_testrun_data = {}

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

payload = {}
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

headers_ai = {
    'Authorization': 'Bearer 1.VvzUpAo8PbdPEcbb2ol96VpcvfI=',
    'Accept': 'application/json',
    'Content-Type': 'application/xml'
}

payload_ai_test_create_template = """<?xml version="1.0" encoding="UTF-8"?>
<Asset href="/HMHealthSolutions/rest-1.v1/New/Test">
	<Attribute name="Name" act="set">""" + ai_test_title + """</Attribute>
	<Attribute name="Description" act="set">""" + ai_test_description + """</Attribute>
    
<!-- Newly created Story -->
    <Relation name="Parent" act="set">
       <Asset href="/HMHealthSolutions/rest-1.v1/Data/Story/""" + ai_test_storyId + """" idref="Story:""" + ai_test_storyId + """" />
    </Relation>
  	<Relation name="Status" act="set">
		<Asset idref="TestStatus:""" + ai_test_status + """" />
	</Relation>
</Asset>
"""


def load_config():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile)

    for section in cfg:
        print(section)
    projIds = cfg["mocks"]["spira"]["project"]
    for projId in projIds:
        print(projId)
    return cfg


def action(url, verb, headers, payload, params):
    # print("\n\nINF: Raw Url: ", url)
    response = requests.request(verb, url, headers=headers, data=payload, params=params)
    print("INF: Request Url: ", response.request.path_url)
    # print("INF: Response Headers: ", response.headers)
    # print("INF: Response Text", response.text)

    return response, response.json()


def ai_create_storylevel_testcase(storyId, title, description, status, owner=""):
    payload_ai_test_create_template = """<?xml version="1.0" encoding="UTF-8"?>
    <Asset href="/HMHealthSolutions/rest-1.v1/New/Test">
        <Attribute name="Name" act="set">""" + title + """</Attribute>
        <Attribute name="Description" act="set">""" + description + """</Attribute>
        
    <!-- Newly created Story -->
        <Relation name="Parent" act="set">
           <Asset href="/HMHealthSolutions/rest-1.v1/Data/Story/""" + storyId + """" idref="Story:""" + storyId + """" />
        </Relation>
        <Relation name="Status" act="set">
            <Asset idref="TestStatus:""" + status + """" />
        </Relation>
    </Asset>
    """
    base_url_ai = "https://www16.v1host.com/api-examples/rest-1.v1"
    url_ai = base_url_ai + "/Data/Test"
    response_ai, result_ai = action(url_ai, verb="POST", headers=headers_ai, payload=payload_ai_test_create_template,
                                    params={})

    testcaseId = result_ai["id"].split(":")[1]
    testcaseMomentId = result_ai["id"].split(":")[2]
    storyId = result_ai["Attributes"]["Parent"]["value"]["idref"].split(":")[1]
    print("INF: ai_storyId: ", storyId)
    print("INF: ai_testcaseId: ", testcaseId)
    print("INF: ai_testcaseMomentId: ", testcaseMomentId)

    return {"testcaseId": testcaseId, "testcaseMomentId": testcaseMomentId, "storyId": storyId}


# Test Case Builder
# Criteria
# Passed / Failed
# Reference story Id from Testcase Loop
def testcase_builder(ai_project, ai_release, testRunTypeId, story_id, tc_id, tr_id, test_status):
    # Update is create?
    # Logic - Update / Create

    project_id = ai_project
    release_id = ai_release
    tr_id = testRunTypeId
    ai_timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ai_test_storyId = story_id
    ai_test_description = "Prog Main Test Desc"
    ai_test_owners = ""
    latest_testrunId = tr_id
    ai_test_title = "CPT Test -" + ai_timestamp + \
                    " SP Source (" + str(ai_test_storyId) + \
                    ":" + \
                    str(tc_id) + \
                    ":" + \
                    str(latest_testrunId) + \
                    ":" + \
                    str(test_status) + \
                    ")"

    # Logic - Execution Status
    # Failed = 1; Passed = 2; NotRun = 3; NotApplicable = 4; Blocked = 5; Caution = 6;
    if test_status == 1:
        ai_test_status = "155"
    else:
        ai_test_status = "129"

    # Logic - Manual / Automated

    ai_create_storylevel_testcase(
        storyId=ai_test_storyId,
        title=ai_test_title,
        description=ai_test_description,
        status=ai_test_status,
        owner=ai_test_owners
    )


# Init Project
cfg = load_config()

sp_params = {
    'username': cfg["spira"]["username"],
    'api-key': cfg["spira"]["api-key"]
}
# Get Spira Project List
base_url = (
        cfg["spira"]["proto"] + "://" +
        cfg["spira"]["host"] + "/" +
        cfg["spira"]["service_instance"]
)

sp_params["starting_row"] = 1
sp_params["number_of_rows"] = 500
######################
# Project Listing
######################
url = base_url + "/projects"
response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)
for item in result:
    print("\nINF: ProjectId: ", str(item["ProjectId"]))
    print("INF: Project Name: ", str(item["Name"]))
    sp_project_data.append({
        "id": item["ProjectId"],
        "name": item["Name"]
    })

rt_mode = "test"
if rt_mode == "test":
    sp_project_data = [{
        "id": 28,
        "name": "Sandbox - Claims Unit and Integration"
    }]
# print(sp_project_data)

######################
# Project Requirements
# Contains Digital AI Story ID?
######################

print("\nProject Requirements: ")
print("Criteria: RequirementTypeName = UserStory")
print("Input: Projects = ", len(sp_project_data))
for rt in sp_project_data:
    print("INF: ProjectId: ", str(rt["id"]))
    print("INF: Project Name: ", str(rt["name"]))
    url = base_url + "/projects/" + str(rt["id"]) + "/requirements"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)
    for item in result:
        print("INF: RequirementId: ", str(item["RequirementId"]))
        # If Req Type User Story
        sp_project_req_data.append({
            "id": item["RequirementId"],
            "projectId": item["ProjectId"],
            "statusId": item["StatusId"],
            "releaseId": item["ReleaseId"],

            "requirementTypeName": item["RequirementTypeName"],
            "projectName": item["ProjectName"],
            "name": item["Name"],
            "description": item["Description"],
            # Test Info / Not Integrity Info
            "coverageCountTotal": item["CoverageCountTotal"],
            "coverageCountPassed": item["CoverageCountPassed"],
            "CoverageCountFailed": item["CoverageCountFailed"],

            "tags": item["Tags"],

            "authorName": item["AuthorName"],
            "ownerName": item["OwnerName"]
        })
# print(sp_project_req_data)


######################
# Project Test Cases
# Get all test for each project
######################

print("\nProject Test Cases: ")
print("Criteria: RequirementTypeName = UserStory")
print("Input: Projects = ", len(sp_project_data))
for rt in sp_project_data:
    print("INF: ProjectId: ", str(rt["id"]))
    print("INF: Project Name: ", str(rt["name"]))
    url = base_url + "/projects/" + str(rt["id"]) + "/test-cases"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    for item in result:
        print("INF: TestCaseId: ", str(item["TestCaseId"]))

        # ai_test_storyId = "8247"
        # ai_test_title = "Prog Main Test" + item["TestCaseId"]
        # ai_test_description = "Prog Main Test Desc" + item["TestCaseId"]
        # ai_create_storylevel_testcase(ai_test_storyId,ai_test_title,ai_test_description)

        sp_project_testcase_data.append({
            "id": item["TestCaseId"],
            "projectId": item["ProjectId"],
            "statusId": item["TestCaseStatusId"],
            "customProperties": item["CustomProperties"],

            "projectName": item["ProjectName"],
            "name": item["Name"],
            "description": item["Description"],
            "tags": item["Tags"],

            "authorName": item["AuthorName"],
            "ownerName": item["OwnerName"]
        })
# print(sp_project_testcase_data)

######################
# Project Test Steps
# Get all test steps for each test case
######################

print("\nProject Test Steps: ")
print("Input: TestCases = ", len(sp_project_testcase_data))
# https://highmarkhealth.spiraservice.net/Services/v6_0/RestService.svc/projects/23/test-cases/1169/test-steps
for rt in sp_project_testcase_data:
    print("INF: ProjectId: ", str(rt["projectId"]))
    print("INF: Project Name: ", str(rt["projectName"]))
    print("INF: TestcaseId: ", str(rt["id"]))
    url = base_url + "/projects/" + str(rt["projectId"]) + "/test-cases/" + str(rt["id"]) + "/test-steps"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    for item in result:
        print("INF: TestStepId: ", str(item["TestStepId"]))
        sp_project_teststep_data.append({
            "id": item["TestStepId"],
            "testCaseId": item["TestCaseId"],
            "projectId": item["ProjectId"],
            "artifactTypeId": item["ArtifactTypeId"],
            "executionStatusId": item["ExecutionStatusId"],

            "description": item["Description"],
            "expectedResult": item["ExpectedResult"],
            "sampleData": item["SampleData"],
            "position": item["Position"],

            "tags": item["Tags"],

            "customProperties": item["CustomProperties"]
        })
# print(sp_project_teststep_data)


######################
# Test Case Runs
# Get all runs for testcase e
######################

print("\n\n\nProject Test Case/Set Runs: ")
print("Input: Project Data = ", len(sp_project_data))
# https://highmarkhealth.spiraservice.net/Services/v6_0/RestService.svc/projects/23/test-cases/1169/test-runs
for rt in sp_project_data:
    print("INF: ProjectId: ", str(rt["id"]))
    print("INF: Project Name: ", str(rt["name"]))
    url = base_url + "/projects/" + str(rt["id"]) + "/test-runs"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    # LIST - test runs in the project
    for item in result:
        print("INF: TestCaseId: ", str(item["TestCaseId"]))
        print("\nINF: TestRunId: ", str(item["TestRunId"]))
        # print("INF: ArtifactTypeId: ", str(item["ArtifactTypeId"]))

        # Map List entries to Dictionary Structure
        x = sp_project_testrun_data.get(item["TestCaseId"])
        if sp_project_testrun_data.get(item["TestCaseId"]) == None:
            sp_project_testrun_data[item["TestCaseId"]] = {}
            sp_project_testrun_data[item["TestCaseId"]].update({item["TestRunId"]: {
                "projectId": item["ProjectId"],
                "artifactTypeId": item["ArtifactTypeId"],
                "releaseId": item["ReleaseId"],
                # TestRunTypeId	The id of the type of test run (automated vs. manual)
                "testRunTypeId": item["TestRunTypeId"],
                # Failed = 1; Passed = 2; NotRun = 3; NotApplicable = 4; Blocked = 5; Caution = 6;
                "executionStatusId": item["ExecutionStatusId"],

                # "endDate": item["EndDate"],

                # "tags": item["Tags"],

                # The list of associated custom properties/fields for this artifact
                # "customProperties": item["CustomProperties"]
            }})
        else:
            sp_project_testrun_data[item["TestCaseId"]].update({item["TestRunId"]: {
                "projectId": item["ProjectId"],
                "artifactTypeId": item["ArtifactTypeId"],
                "releaseId": item["ReleaseId"],
                # TestRunTypeId	The id of the type of test run (automated vs. manual)
                "testRunTypeId": item["TestRunTypeId"],
                # Failed = 1; Passed = 2; NotRun = 3; NotApplicable = 4; Blocked = 5; Caution = 6;
                "executionStatusId": item["ExecutionStatusId"],

                # "endDate": item["EndDate"],

                # "tags": item["Tags"],

                # The list of associated custom properties/fields for this artifact
                # "customProperties": item["CustomProperties"]
            }})

pprint.pprint(sp_project_testrun_data)


######################
# Post Processing - Test Case Runs
# Get The Latest Test Run/TestCase and Update Agility
######################
print("\n\nINF: Starting Test Execution Analysis")
for tc_id in sp_project_testrun_data:
    tr_dic = sp_project_testrun_data[tc_id]
    tr_ids = list(tr_dic)
    tr_id_size = len(tr_ids)
    print("\nINF: Test Case Id (", tc_id, ")")
    print("INF: Test Run Size (", tr_id_size, ")")

    # Algorithm - Latest Test Run
    tr_id_earliest = sorted(list(tr_dic))[0]
    print("INF: Test Run Earliest (", tr_id_earliest, ")")
    tr_id_latest = sorted(list(tr_dic))[len(tr_ids) - 1]
    print("INF: Test Run Latest (", tr_id_latest, ")")

    # Attributes - Status, Project and Release Id, RunType!
    test_status = sp_project_testrun_data[tc_id][tr_id_latest]["executionStatusId"]
    ai_project = sp_project_testrun_data[tc_id][tr_id_latest]["projectId"]
    ai_release = sp_project_testrun_data[tc_id][tr_id_latest]["releaseId"]
    testRunTypeId = sp_project_testrun_data[tc_id][tr_id_latest]["testRunTypeId"]

    # Logic - Create/Update Testcase
    if tr_id_size == 1:
        mode="create"
    else:
        mode="update"
    testcase_builder(mode, ai_project, ai_release, testRunTypeId, ai_test_storyId, tc_id, tr_id_latest, test_status)

exit("End Of Sync")
