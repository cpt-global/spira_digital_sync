import operator
import pprint
import types
from collections import OrderedDict
from datetime import datetime

import requests
import simplejson
import yaml
import json

# Globals
ai_test_storyId = "8247"
ai_test_title = ""
ai_test_description = ""
ai_test_status = ""
ai_test_owners = ""
ai_test_owner_id = ""

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


def dump_model(project_id, dic):
    fn = str(project_id) + "_" + "rt_model.json"
    fh = open(fn, "w")
    fh.write(simplejson.dumps(dic, indent=4, sort_keys=True))
    fh.close()

    return fh


def write_down(project_id, dic):
    fn = str(project_id) + "_" + "testcases_created.json"
    # x = json.dump(dic, open(fn, 'w'))

    # now write output to a file
    fh = open(fn, "a")
    # magic happens here to make it pretty-printed
    fh.write(simplejson.dumps(dic, indent=4, sort_keys=True))
    fh.close()

    return fh


lookup_dic = {}


def lookup(project_id, tc_id):
    # Case . Epoch - No Sp/Agility Testcases exist
    # Case . A Single SP/A exists
    # Case . Many SP/A exists

    fn = str(project_id) + "_" + "testcases_created.json"
    dic = {}
    ai_tc_id = None
    dic = json.load(open(fn))
    if len(dic) == 0:
        return None
    else:
        # Ok So we have a dic to examine.
        # q. does key exist
        x = dic.get(str(tc_id))

        # No
        if x == None:
            return dic
        # Yes
        else:
            ai_tc_dic = dic[str(tc_id)]
            ai_tc_id = ai_tc_dic['ai_tc_id']
            return ai_tc_id


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
    response_ai, result_ai = action(
        url_ai,
        verb="POST",
        headers=headers_ai,
        payload=payload_ai_test_create_template,
        params={}
    )

    testcaseId = result_ai["id"].split(":")[1]
    testcaseMomentId = result_ai["id"].split(":")[2]
    storyId = result_ai["Attributes"]["Parent"]["value"]["idref"].split(":")[1]
    print("INF: ai_storyId: ", storyId)
    print("INF: ai_testcaseId: ", testcaseId)
    print("INF: ai_testcaseMomentId: ", testcaseMomentId)

    return {"testcaseId": testcaseId, "testcaseMomentId": testcaseMomentId, "storyId": storyId}


def ai_update_storylevel_testcase(tc_id, title, description, status, owner=""):
    payload_ai_test_update_template = """<Asset>
    <Attribute name="Description" act="set">Modified Desciption V2</Attribute>
    </Asset>
    """
    pprint.pprint(payload_ai_test_update_template)
    base_url_ai = "https://www16.v1host.com/api-examples/rest-1.v1"
    url_ai = base_url_ai + "/Data/Test/" + str(tc_id)
    response_ai, result_ai = action(
        url_ai,
        verb="POST",
        headers=headers_ai,
        payload=payload_ai_test_update_template,
        params={}
    )

    testcaseId = result_ai["id"].split(":")[1]
    testcaseMomentId = result_ai["id"].split(":")[2]
    print("INF: ai_testcaseId: ", testcaseId)
    print("INF: ai_testcaseMomentId: ", testcaseMomentId)

    return {"testcaseId": testcaseId, "testcaseMomentId": testcaseMomentId}


# Test Case Builder
# Criteria
# Passed / Failed
# Reference story Id from Testcase Loop
def testcase_builder(mode, ai_project, ai_release, testRunTypeId, story_id, tc_id, tr_id, test_status):
    project_id = ai_project
    release_id = ai_release
    testrun_type_id = testRunTypeId

    ai_timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ai_test_storyId = story_id
    ai_test_description = "Prog Main Test Desc"
    ai_test_owners = "80027"
    latest_testrunId = tr_id
    ai_test_title = mode + " - CPT Test -" + ai_timestamp + \
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


# Init Project
cfg = load_config()

sp_scope_project = cfg["spira"]["scope"]["project_scope"]
sp_scope_requirement_type = cfg["spira"]["scope"]["requirement_type"]
sp_scope_test_type = cfg["spira"]["scope"]["test_type"]
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
rt_model = {}
rt_ai_model = {}
######################
# Project Listing
######################
url = base_url + "/projects"
response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)
for item in result:
    print("\n\n\nINF: Filtering ProjectId For Runtime Acceptance: ", str(item["ProjectId"]))

    if item["ProjectId"] not in sp_scope_project:
        continue;

    print("INF: ProjectId Accepted: ", str(item["ProjectId"]))

    rt_model.update({item["ProjectId"]: {
        "00_info": "!!!Project!!!",
        "name": item["Name"]
    }})
    # print(sp_project_data)
    # pprint.pprint(rt_model)

    ######################
    # Project Requirements
    # Contains Digital AI Story ID?
    ######################

    print("\nProject Requirements: ")
    print("Criteria: RequirementTypeName = UserStory")
    url = base_url + "/projects/" + str(item["ProjectId"]) + "/requirements"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)
    for item in result:
        print("INF: RequirementId: ", str(item["RequirementId"]))
        # If Req Type User Story

        if item["RequirementTypeName"] == sp_scope_requirement_type:
            rt_model.update({
                    item["RequirementId"] :{
                    "00_info": "!!!Requirement!!!",
                    # "id": item["RequirementId"],
                    "projectId": item["ProjectId"],
                    "statusId": item["StatusId"],
                    "releaseId": item["ReleaseId"],
                    "artifactTypeId": item["ArtifactTypeId"],

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
            }})
        # pprint.pprint(rt_model)
    ######################
    # Project Test Cases
    # Get all test for each project
    ######################
    print("\nProject Test Cases: ")
    print("Criteria: RequirementTypeName = UserStory")
    url = base_url + "/projects/" + str(item["ProjectId"]) + "/test-cases"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    for item in result:
        print("INF: TestCaseId: ", str(item["TestCaseId"]))

        ai_test_storyId = item["CustomProperties"][6]["StringValue"]
        ai_test_story_name = item["CustomProperties"][6]["Definition"]["Name"]
        ai_test_requirementId = item["CustomProperties"][7]["StringValue"]
        ai_test_requirement_name = item["CustomProperties"][7]["Definition"]["Name"]

        # rt_ai_model[item["ProjectId"]].update({
        #     item["TestCaseId"]: {
        #         "storyId": ai_test_storyId,
        #         "requirementId": ai_test_requirementId
        #     }
        # })

        rt_model.update({
            item["TestCaseId"]: {
                    "00_info": "!!!Test Case!!!",
                    "id": item["TestCaseId"],
                    "projectId": item["ProjectId"],
                    "statusId": item["TestCaseStatusId"],
                    "customProperties": item["CustomProperties"],
                    "storyId": ai_test_storyId,
                    "requirementId": ai_test_requirementId,
                    "artifactTypeId": item["ArtifactTypeId"],

                    "projectName": item["ProjectName"],
                    "name": item["Name"],
                    "description": item["Description"],
                    "tags": item["Tags"],

                    "authorName": item["AuthorName"],
                    "ownerName": item["OwnerName"]
                }})
        # pprint.pprint(rt_model)

        ######################
        # Project Test Steps
        # Get all test steps for each test case
        ######################

        print("\nProject Test Steps: ")
        print("Input: TestCases = ", len(sp_project_testcase_data))
        # https://highmarkhealth.spiraservice.net/Services/v6_0/RestService.svc/projects/23/test-cases/1169/test-steps
        print("INF: TestcaseId: ", str(item["TestCaseId"]))
        url = base_url + "/projects/" + str(item["ProjectId"]) + "/test-cases/" + str(
            item["TestCaseId"]) + "/test-steps"
        response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

        for item in result:
            print("INF: TestStepId: ", str(item["TestStepId"]))
            # rt_model[item["ProjectId"]][item["TestCaseId"]].update({
            rt_model.update({
                item["TestStepId"]: {
                    "00_info": "!!!Test Step!!!",
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
                }})
        pprint.pprint(rt_model)

    ######################
    # Test Case Runs
    # Get all runs for testcase
    ######################

    print("\nProject Test Case/Set Runs: ")
    url = base_url + "/projects/" + str(item["ProjectId"]) + "/test-runs"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    # LIST - test runs in the project
    for item in result:
        print("INF: TestCaseId: ", str(item["TestCaseId"]))
        print("INF: TestRunId: ", str(item["TestRunId"]))

        # rt_model[item["ProjectId"]][item["TestCaseId"]].update({
        rt_model.update({
            item["TestRunId"]: {
                "00_info": "!!!Test Run!!!",
                "TestCaseId": item["TestCaseId"],
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
                "customProperties": item["CustomProperties"]
            }})

    dump_model(item["ProjectId"], rt_model)

######################
# Post Processing - Test Case Runs
# Get The Latest Test Run/TestCase and Update Agility
######################
print("\n\nINF: Starting Test Execution Analysis")
NumberTypes = (int, float, complex)

for rt_project_item in rt_model:
    rt_project_dic = rt_model.get(rt_project_item)

    for rt_project_artifact_id in rt_project_dic:


        # Just interested in artifact Ids
        if isinstance(rt_project_artifact_id, NumberTypes):
            rt_project_artifact_dic = rt_project_dic.get(rt_project_artifact_id)
            tc_id = rt_project_artifact_id

            # Is Testable Artifact Type?
            if rt_project_artifact_dic["artifactTypeId"] == 2:

                # Is Test Run
                for rt_tc_artifact_entries in rt_project_artifact_dic:
                        tr_id = rt_tc_artifact_entries

                    # Just interested in artifact Ids
                        if isinstance(rt_tc_artifact_entries, NumberTypes):
                            # Is Id Test Run or Test Step?
                            if rt_project_artifact_dic[rt_tc_artifact_entries]["artifactTypeId"] == 5:
                                print("INF: TestRun Level Identified ", )

                                # Explore Level!!!
                                ts = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

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
                                projectId = sp_project_testrun_data[tc_id][tr_id_latest]["projectId"]
                                ai_release = sp_project_testrun_data[tc_id][tr_id_latest]["releaseId"]
                                testRunTypeId = sp_project_testrun_data[tc_id][tr_id_latest]["testRunTypeId"]

                                # Build Debug Title
                                title = " - CPT Test - "
                                title += ts
                                title += " SP (" + str(ai_test_storyId)
                                title += ":" + str(tc_id) + ":" + str(tr_id_latest) + ":" + str(test_status) + ")"

                                # Logic - Execution Status
                                # Failed = 1; Passed = 2; NotRun = 3; NotApplicable = 4; Blocked = 5; Caution = 6;
                                if test_status == 1:
                                    ai_test_status = "155"
                                else:
                                    ai_test_status = "129"

                                # Logic - Create/Update Testcase
                                if tr_id_size == 1:
                                    mode = "create"
                                    title += mode
                                    # Compose TC Attributes
                                    ai_test_description = "Prog Main Test Desc"
                                    ai_test_owners = "80027"

                                    # Lookup Story Id for Testcase
                                    ai_test_storyId = story_id
                                    url = base_url + "/projects/26/test-cases"
                                    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

                                    # Lookup Logic
                                    # - Load existing if any
                                    # - add new entry to log
                                    # - refresh log with new entry
                                    lookup_dic = lookup(projectId, tc_id)
                                    lookup_dic.update({tc_id: {"ai_tc_id": 8288, "ai_tc_title": "xxxx", "state": False}})
                                    write_down(projectId, lookup_dic)

                                    testcaseId, testcaseMomentId, storyId = ai_create_storylevel_testcase(
                                        storyId=ai_test_storyId,
                                        title=title,
                                        description=ai_test_description,
                                        status=ai_test_status,
                                        owner=ai_test_owners)
                                else:
                                    mode = "update"
                                    title += mode
                                    # Lookup Logic
                                    # Retrieve _existing_ SP/A pairing
                                    lookup_ai_tc_id = lookup(projectId, tc_id)

                                    testcaseId, testcaseMomentId, storyId = ai_create_storylevel_testcase(
                                        storyId=ai_test_storyId,
                                        title=title,
                                        description=ai_test_description,
                                        status=ai_test_status,
                                        owner=ai_test_owners)

exit("End Of Sync")
