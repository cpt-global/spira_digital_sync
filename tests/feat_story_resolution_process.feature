# Created by ennisa at 14/09/2022
Feature: Resolution of test runs per story
  This logic is intended to set up a filter and assign a suitable story status based on the results of zero or more test execution result status

  Scenario Outline: Single Story with a single testcase with NO test runs associated with it
    Given I have a story <story_id> with a test case <tc_id>
    And no test run <tr_id> associated with it
    Then I expect a story resolution status <story_resolution_id>

    Examples: Functional Test Case
      | story_id | tc_id | tr_id | story_resolution_id |
      | 8355     | 3716  | None  | None                |

  Scenario Outline: Single Story with single testcase with a single test run(Passed) associated with it
    Given I have a story <story_id> with a test case <tc_id>
    And a single test run <tr_id> associated with it that passes
    Then I expect a story resolution status <story_resolution_id>

    Examples: Functional Test Case
      | story_id | tc_id | tr_id | story_resolution_id |
      | 8357     | 3717  | 2694   | Done                |

  Scenario Outline: Single Story with single testcase with a single test run(Failed) associated with it
    Given I have a story <story_id> with a test case <tc_id>
    And a single test run <tr_id> associated with it that passes
    Then I expect a story resolution status <story_resolution_id>

    Examples: Functional Test Case
      | story_id | tc_id | tr_id | story_resolution_id |
      | 8351     | 3713  | 223   | InProgress          |

  Scenario Outline: Single Story with more than one testcase each testcase has a single test run associated with it
    Given I have a story <story_id> with a test case <tc_id>
    And a single test run <tr_id> associated with it that passes
    Then I expect a story resolution status <story_resolution_id>

    Examples: Functional Test Case
      | story_id | tc_id | tr_id | story_resolution_id |


