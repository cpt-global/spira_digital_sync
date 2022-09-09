import collections
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


def sp_get_project_test_runs(model, project_id):
    print("\nProject Test Case/Set Runs: ")
    url = base_url + "/projects/" + str(project_id) + "/test-runs"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    # LIST - test runs in the project
    for item in result:
        print("INF: TestCaseId: ", str(item["TestCaseId"]))
        print("INF: TestRunId: ", str(item["TestRunId"]))

        # Only Testcases that are valid (in the model already)
        if model.get(item["TestCaseId"]) != None:
            print("INF: Coupling Test Run ", item["TestRunId"], "With Valid Testcase ", item["TestCaseId"])

            model.update({
                item["TestRunId"]: {
                    "00_info": "!!!Test Run!!!",
                    "testCaseId": item["TestCaseId"],
                    "testRunId": item["TestRunId"],
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

    return model


def sp_get_project_requirements(model, project_id):
    print("\nProject Requirements: ")
    print("Criteria: RequirementTypeName = UserStory")
    url = base_url + "/projects/" + str(project_id) + "/requirements"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)
    for item in result:
        print("INF: RequirementId: ", str(item["RequirementId"]))
        # If Req Type User Story

        if item["RequirementTypeName"] == sp_scope_requirement_type:
            model.update({
                item["RequirementId"]: {
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

    return model


def sp_get_project_test_cases(model, project_id):
    print("\nProject Test Cases: ")
    print("Criteria: RequirementTypeName = UserStory")
    url = base_url + "/projects/" + str(project_id) + "/test-cases"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    for item in result:
        print("INF: TestCaseId: ", str(item["TestCaseId"]))

        ai_test_storyId = item["CustomProperties"][6]["StringValue"]
        ai_test_story_name = item["CustomProperties"][6]["Definition"]["Name"]
        ai_test_requirementId = item["CustomProperties"][7]["StringValue"]
        ai_test_requirement_name = item["CustomProperties"][7]["Definition"]["Name"]

        if ai_test_storyId != None:
            # Create TestCase
            # ai_test_create_dic = ai_create_storylevel_testcase(
            #     storyId=ai_test_storyId,
            #     title=item["Name"],
            #     description=item["Description"],
            #     # Default Failed/Empty
            #     status="155"
            # )

            # Add Agility TestCase Id To model for update report
            model.update({
                item["TestCaseId"]: {
                    "00_info": "!!!Test Case!!!",
                    "testCaseId": item["TestCaseId"],
                    # "testCaseId_Agility": ai_test_create_dic["testcaseId"],
                    "testCaseId_Agility": 8310,
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

    # rt_model = sp_get_project_test_steps(rt_model, item["ProjectId"], item["TestCaseId"])

    return model


def sp_get_project_test_steps(model, project_id, tc_id):
    print("\nProject Test Steps: ")
    print("Input: TestCases = ", len(sp_project_testcase_data))
    # https://highmarkhealth.spiraservice.net/Services/v6_0/RestService.svc/projects/23/test-cases/1169/test-steps
    print("INF: TestcaseId: ", str(tc_id))
    url = base_url + "/projects/" + str(project_id) + "/test-cases/" + str(tc_id) + "/test-steps"
    response, result = action(url, verb="GET", headers=headers, payload=payload, params=sp_params)

    for item in result:
        print("INF: TestStepId: ", str(item["TestStepId"]))
        # rt_model[item["ProjectId"]][item["TestCaseId"]].update({
        model.update({
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
    # pprint.pprint(rt_model)
    return model


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


def ai_create_storylevel_testcase(storyId, title, description, status):
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

    return {"testcaseId": testcaseId, "testcaseMomentId": testcaseMomentId}


def ai_update_storylevel_testcase(tc_id, status):
    payload_ai_test_update_template = """<Asset>
    <Attribute name="Description" act="set">Modified Description V2</Attribute>
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
    # print("INF: ai_testcaseId: ", testcaseId)
    # print("INF: ai_testcaseMomentId: ", testcaseMomentId)

    return {"momentId": testcaseMomentId}


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

    ######################
    # Project Requirements
    # Contains Digital AI Story ID?
    ######################
    rt_model = sp_get_project_requirements(rt_model, item["ProjectId"])
    # pprint.pprint(rt_model)

    ######################
    # Project Test Cases
    # Get all test for each project
    ######################
    rt_model = sp_get_project_test_cases(rt_model, item["ProjectId"])
    # pprint.pprint(rt_model)

    ######################
    # Test Case Runs
    # Get all runs for testcase
    ######################
    rt_model = sp_get_project_test_runs(rt_model, item["ProjectId"])

    dump_model(item["ProjectId"], rt_model)

######################
# Post Processing - Test Case Runs
# Get The Latest Test Run/TestCase and Update Agility
######################
print("\n\nINF: Starting Test Execution Analysis")
NumberTypes = (int, float, complex)

rt_ai_model = OrderedDict()
for artifact_id in rt_model:
    artifact_dic = rt_model.get(artifact_id)

    if artifact_dic["artifactTypeId"] == cfg["spira"]["artifact_ids"]["test_case"]:
        tc_id = artifact_dic["testCaseId"]
        tc_id_ai = rt_model[tc_id]["testCaseId_Agility"]
        storyId = rt_model[tc_id]["storyId"]
        requirementId = rt_model[tc_id]["requirementId"]
        rt_ai_model.update({
            tc_id: {
                "storyId_ai": storyId,
                "testcaseId_id": tc_id_ai,
                "requirementId": requirementId,
            }
        })
        print("TC ID ", tc_id)
        print("Story ID ", storyId)
        print("Req ID ", requirementId)

    # Is Test Run Artifact Type?
    if artifact_dic["artifactTypeId"] == cfg["spira"]["artifact_ids"]["test_run"]:
        print("INF: TestRun Level Identified ")
        ts = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        tc_id = artifact_dic["testCaseId"]

        tc_execution_status_id = artifact_dic["executionStatusId"]
        tr_id = artifact_id
        rt_ai_model[tc_id].update({
            tr_id: {
                "executionStatusId": tc_execution_status_id
            }
        })

        # storyId = rt_model[tc_id]
        print("TC Run and Status ID ", tr_id, "-", tc_execution_status_id)

    else:
        print("INF: Not TestRun, if TC then create? ")

#
# RT Model Analysis For Agility Information
#
pprint.pprint(rt_ai_model)
# pprint.pprint( list(rt_ai_model.items())[0])
print("")
print("INF: Number TestCase To Process ", len(list(rt_ai_model.items())))
for tcId, tcDic in reversed(list(rt_ai_model.items())):
    # print(type(tcData))
    # print(type(trData))
    # pprint.pprint(tcId)
    # pprint.pprint(tcDic)
    storyId_ai = tcDic.get("storyId_ai")
    print("INF: Story Id", storyId_ai)
    requirementId = tcDic.get("requirementId")
    print("INF: Requirement Id", requirementId)
    testcaseId_ai = tcDic.get("testcaseId_id")
    print("INF: Test Id Agility", testcaseId_ai)

    for item in collections.OrderedDict(reversed(list(tcDic.items()))):
        # pprint.pprint(item)
        if isinstance(item, NumberTypes):
            # Found some test runs
            tr_id = item
            tr_exec_id = tcDic.get(item)["executionStatusId"]
            print("INF: Test Run Id", tr_id, "Execution Status", tr_exec_id)
            tc_moment_id = ai_update_storylevel_testcase(tc_id=tc_id_ai, status=tr_exec_id)["momentId"]
            print("INF: Test Moment Id", tc_moment_id)

            # if execution status is passed do we close story?
