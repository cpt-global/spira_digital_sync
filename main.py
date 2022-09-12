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
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

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

NumberTypes = (int, float, complex)


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

        ai_storyId = item["CustomProperties"][6]["StringValue"]
        ai_test_story_name = item["CustomProperties"][6]["Definition"]["Name"]
        ai_test_requirementId = item["CustomProperties"][7]["StringValue"]
        ai_test_requirement_name = item["CustomProperties"][7]["Definition"]["Name"]

        # Logic: Testcase StoryId mapping exists
        if ai_storyId != None:
            # Does SP Testcase have an agility TC?
            response_agility_tc_id, response_dic = lookup(item["ProjectId"], item["TestCaseId"])

            # Ok
            # 1. create agility testcase
            # - ref to TC
            # - ref to Req?
            # 2. update record log
            # 3. update model for downstream processing
            # Logic: Lookup table /
            if response_agility_tc_id == None:

                # 1. create agility testcase with reference details
                integrity_link_tc = "https://highmarkhealth.spiraservice.net/" + str(
                    item["ProjectId"]) + "/TestCase/" + str(item["TestCaseId"]) + "/Overview.aspx"
                item["Description"] += "&lt;br&gt;"
                item["Description"] += "&lt;br&gt;"
                item["Description"] += "&lt;strong&gt;"
                item["Description"] += "Spira Plan Reference(s)"
                item["Description"] += "&lt;strong&gt;"
                item["Description"] += "&lt;br&gt;"

                html_builder = "&lt;a"
                html_builder += " href=\""
                html_builder += integrity_link_tc
                html_builder += "\""
                html_builder += " target=\"_blank\""
                html_builder += "&gt;"
                html_builder += "Testcase Link: (" + item["Name"] + "...)"
                html_builder += "&lt;"
                html_builder += "/a"
                html_builder += "&gt;"

                item["Description"] += html_builder

                item["Description"] += "&lt;br&gt;"

                ai_tc_dic = ai_create_storylevel_testcase(
                    storyId=ai_storyId,
                    title=item["Name"],
                    description=item["Description"]
                )

                # 2. update record json log!
                response_dic.update({
                    item["TestCaseId"]: {
                        "tc_id_ai": int(ai_tc_dic["testcaseId"]),
                        "moment_id_ai": int(ai_tc_dic["momentId"]),
                        "storyId_ai": int(ai_storyId),
                        "tc_status_id": int(item["TestCaseStatusId"]),
                        "lc": 1}
                })
                write_down(item["ProjectId"], response_dic)

                # 3. update model for downstream processing
                tc_model_item = {
                    item["TestCaseId"]: {
                        "00_info": "!!!Test Case!!!",
                        "testCaseId": item["TestCaseId"],
                        # "testCaseId_Agility": 8310,
                        "testCaseId_Agility": ai_tc_dic["testcaseId"],
                        "momentId_Agility": ai_tc_dic["momentId"],
                        "projectId": item["ProjectId"],
                        "statusId": item["TestCaseStatusId"],
                        "customProperties": item["CustomProperties"],
                        "storyId": ai_storyId,
                        "requirementId": ai_test_requirementId,
                        "artifactTypeId": item["ArtifactTypeId"],

                        "projectName": item["ProjectName"],
                        "name": item["Name"],
                        "description": item["Description"],
                        "tags": item["Tags"],

                        "authorName": item["AuthorName"],
                        "ownerName": item["OwnerName"]
                    }}
                model.update(tc_model_item)
            # pprint.pprint(rt_model)
            else:
                print("INF: Agility testcase already created")
                # Lets use the log tests so that test run can process something!
                # "testCaseId_Agility": 8310,
                tc_model_item = {
                    item["TestCaseId"]: {
                        "00_info": "!!!Test Case!!!",
                        "testCaseId": item["TestCaseId"],
                        "storyId": ai_storyId,
                        "testCaseId_Agility": response_agility_tc_id,
                        "momentId_Agility": response_dic.get(str(item["TestCaseId"]))["moment_id_ai"],
                        "statusId": item["TestCaseStatusId"],
                        "requirementId": ai_test_requirementId,
                        "artifactTypeId": item["ArtifactTypeId"],

                        "projectName": item["ProjectName"],
                        "name": item["Name"],
                        "description": item["Description"],
                        "tags": item["Tags"],

                        "authorName": item["AuthorName"],
                        "ownerName": item["OwnerName"],

                        "customProperties": item["CustomProperties"]
                    }}
                model.update(tc_model_item)

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
    fh = open(fn, "w")
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
    record_log = {}
    ai_tc_id = None
    record_log = json.load(open(fn))
    # q. does key exist
    x = record_log.get(str(tc_id))

    # No
    if x is None:
        return None, record_log
    # Yes
    else:
        ai_tc_dic = record_log[str(tc_id)]
        ai_tc_id = ai_tc_dic['tc_id_ai']
        return ai_tc_id, record_log


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


def ai_update_story(storyId, status):
    payload_ai_story_update_template = """<Asset>
        <Relation name="Status" act="set">
            <Asset idref="StoryStatus:""" + str(status) + """" />
        </Relation>
    </Asset>
    """
    pprint.pprint(payload_ai_story_update_template)
    base_url_ai = "https://www16.v1host.com/api-examples/rest-1.v1"
    url_ai = base_url_ai + "/Data/Story/" + str(storyId)
    response_ai, result_ai = action(
        url_ai,
        verb="POST",
        headers=headers_ai,
        payload=payload_ai_story_update_template,
        params={}
    )

    storyId = result_ai["id"].split(":")[1]
    momentId = result_ai["id"].split(":")[2]

    return {"momentId": momentId}


def ai_create_storylevel_testcase(storyId, title, description):
    payload_ai_test_create_template = """<?xml version="1.0" encoding="UTF-8"?>
    <Asset href="/HMHealthSolutions/rest-1.v1/New/Test">
        <Attribute name="Name" act="set">""" + title + """</Attribute>
        <Attribute name="Description" act="set">""" + description + """</Attribute>
        
    <!-- Newly created Story -->
        <Relation name="Parent" act="set">
           <Asset href="/HMHealthSolutions/rest-1.v1/Data/Story/""" + storyId + """" idref="Story:""" + storyId + """" />
        </Relation>
    </Asset>
    """

    # Filter non break spaces
    payload = payload_ai_test_create_template.replace("&nbsp;", "").replace("<br>", "&lt;br&gt;")
    base_url_ai = "https://www16.v1host.com/api-examples/rest-1.v1"
    url_ai = base_url_ai + "/Data/Test"
    response_ai, result_ai = action(
        url_ai,
        verb="POST",
        headers=headers_ai,
        payload=payload,
        params={}
    )

    testcaseId = result_ai["id"].split(":")[1]
    testcaseMomentId = result_ai["id"].split(":")[2]
    storyId = result_ai["Attributes"]["Parent"]["value"]["idref"].split(":")[1]
    print("INF: ai_testcaseId: ", testcaseId)
    print("INF: ai_testcaseMomentId: ", testcaseMomentId)

    return {"testcaseId": testcaseId, "momentId": testcaseMomentId}


def ai_update_storylevel_testcase(tc_id, status):
    # <Attribute name="Description" act="set">Modified Description V2</Attribute>
    payload_ai_test_update_template = """<Asset>
        <Relation name="Status" act="set">
            <Asset idref="TestStatus:""" + str(status) + """" />
        </Relation>
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


def ai_query_storylevel_testcase(tc_id):
    # <Attribute name="Description" act="set">Modified Description V2</Attribute>
    base_url_ai = "https://www16.v1host.com/api-examples/rest-1.v1"
    url_ai = base_url_ai + "/Data/Test/" + str(tc_id)
    response_ai, result_ai = action(
        url_ai,
        verb="GET",
        headers=headers_ai,
        payload={},
        params={}
    )

    testcaseId = result_ai["id"].split(":")[1]
    # testcaseMomentId = result_ai["id"].split(":")[2]

    return result_ai


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
rt_model_sp = {}
rt_ai_model = {}

freq = cfg["spira"]["polling"]["frequency"]


def sp_2_ai_update_testcase_builder(rt_model_sp):
    rt_ai_model = OrderedDict()

    for artifact_id in rt_model_sp:
        artifact_dic = rt_model_sp.get(artifact_id)

        if artifact_dic["artifactTypeId"] == cfg["spira"]["artifact_ids"]["test_case"]:
            tc_id = artifact_dic["testCaseId"]
            tc_id_ai = rt_model_sp[tc_id]["testCaseId_Agility"]
            storyId = rt_model_sp[tc_id]["storyId"]
            requirementId = rt_model_sp[tc_id]["requirementId"]
            rt_ai_model.update({
                tc_id: {
                    "storyId_ai": storyId,
                    "testcaseId_id": tc_id_ai,
                    "requirementId": requirementId,
                    "tr_ids": {
                    }
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
            rt_ai_model[tc_id]["tr_ids"].update({
                tr_id: {
                    "executionStatusId": tc_execution_status_id
                }
            })

            # storyId = rt_model[tc_id]
            print("TC Run and Status ID ", tr_id, "-", tc_execution_status_id)

        else:
            print("INF: Not TestRun, if TC then create? ")

    return rt_ai_model


# scheduler = BlockingScheduler()
# @scheduler.scheduled_job(IntervalTrigger(seconds=freq))
######################
# Project Listing
######################
def sp_poll(rt_model):
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
        # rt_model = sp_get_project_test_steps(rt_model, item["ProjectId"], item["TestCaseId"])

        ######################
        # Test Case Runs
        # Get all runs for testcase
        ######################
        rt_model = sp_get_project_test_runs(rt_model, item["ProjectId"])

        ###
        dump_model(item["ProjectId"], rt_model)

        return rt_model


######################
# Processing - Reqs / Testcase Analysis
# Filter out valid req / testcases pairs
######################
rt_model_sp = sp_poll(rt_model_sp)

######################
# Post Processing - Test Case Runs
# - Build Agility Update Testcase Model
# - Sort / Get The Latest Test Run/TestCase
######################
print("\n\nINF: Starting Test Execution Analysis")
rt_ai_model = sp_2_ai_update_testcase_builder(rt_model_sp)

#
# RT Model Analysis For Agility Information
#
print("\n\n\nINF: Agility Test Run Processing ")
print("INF: Model Under inspection  ")
pprint.pprint(rt_ai_model)
process_queue_size = len(list(rt_ai_model.items()))
print("INF: Processing Queue Size ", process_queue_size)
if process_queue_size > 0:
    for tcId, tcDic in reversed(list(rt_ai_model.items())):
        storyId_ai = tcDic.get("storyId_ai")
        print("\nINF: Story Id", storyId_ai)
        requirementId = tcDic.get("requirementId")
        print("INF: Requirement Id", requirementId)
        testcaseId_ai = tcDic.get("testcaseId_id")
        print("INF: Test Id Agility", testcaseId_ai)

        # Sieve through the runtime list items
        for item in collections.OrderedDict(reversed(list(tcDic.get('tr_ids').items()))):
            # pprint.pprint(item)
            # tr_ids_dic = tcDic.get('tr_ids')
            # if tr_ids_dic is not None:
            # if isinstance(item, NumberTypes):
            # Found some test runs!
            tr_id = item
            # tr_exec_id = tcDic['tr_ids'].get(item)
            tr_exec_id = tcDic['tr_ids'].get(item)["executionStatusId"]

            # Assign Agility Pass/Fail Id
            # Failed = 1; Passed = 2; NotRun = 3; NotApplicable = 4; Blocked = 5; Caution = 6;
            if tr_exec_id == 2:
                ai_test_status = cfg["digital"]["test"]["status"]["passId"]
            else:
                ai_test_status = cfg["digital"]["test"]["status"]["failId"]

            print("INF: Test Run Id", tr_id, "Execution Status", tr_exec_id)
            tc_moment_id = ai_update_storylevel_testcase(tc_id=testcaseId_ai, status=ai_test_status)["momentId"]
            print("INF: Test Moment Id", tc_moment_id)

else:
    print("INF: Queue Is Empty", process_queue_size)

# story_scope=1476
# https://www16.v1host.com/api-examples/rest-1.v1/Data/Story/8247/Scope
# https://www16.v1host.com/api-examples/rest-1.v1/Data/Scope/1476/Workitems:Test
#####
# Story Level Processing
#####
# - Flatten Test run results to single value

rt_story_status = {}
for tcId, tcDic in reversed(list(rt_ai_model.items())):
    testcaseId_ai = tcDic.get("testcaseId_id")
    print("\nINF: Test Id Agility", testcaseId_ai)
    storyId_ai = tcDic.get("storyId_ai")
    print("INF: Story Id", storyId_ai)
    # https://www16.v1host.com/api-examples/rest-1.v1/Data/Test/8339/Status.Name

    tc_response = ai_query_storylevel_testcase(tc_id=testcaseId_ai)

    tc_execution_status_ai = tc_response["Attributes"]["Status.Name"]["value"]

    # If any of the stories testcases fail, then whole story fails
    rt_story_status[int(storyId_ai)] = 1
    if tc_execution_status_ai == "Failed":
        rt_story_status[int(storyId_ai)] -= 1
        continue

pprint.pprint(rt_story_status)
# For each Story update!!!

for storyId_ai, storyId_ai_agg_test_status in rt_story_status.items():

    # Failed
    if storyId_ai_agg_test_status == 0:
        rt_status = cfg["digital"]["story"]["status"]["in_progress"]
        story_moment_id = ai_update_story(storyId=storyId_ai, status=rt_status)["momentId"]
    # All Passed
    else:
        rt_status = cfg["digital"]["story"]["status"]["done"]
        story_moment_id = ai_update_story(storyId=storyId_ai, status=rt_status)["momentId"]

    print("\nINF: Story(Done) Moment Id", story_moment_id)

# scheduler.start()
