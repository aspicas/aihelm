Feature: Task Deletion
  As a developer
  I want to delete tasks from the queue
  So that I can remove tasks I no longer need

  Background:
    Given an empty task queue

  Scenario: Delete a queued task
    When I add a task with name "Unwanted" prompt "p" and branch "feature/unwanted"
    And I delete the task
    Then the queue contains 0 tasks

  Scenario: Reject deleting a running task
    Given a running task with name "Active" prompt "p" and branch "feature/active"
    When I try to delete the task
    Then I receive a validation error containing "Cannot delete a running task"

  Scenario: Deleted task releases branch for reuse
    When I add a task with name "First" prompt "p" and branch "feature/reuse"
    And I delete the task
    And I add a task with name "Second" prompt "p2" and branch "feature/reuse"
    Then the queue contains 1 task
    And the task has name "Second"

  Scenario: Deletion persists across restarts
    Given a JSON-backed task queue
    When I add a task with name "Temp" prompt "p" and branch "feature/temp"
    And I delete the task
    And I reload the queue from storage
    Then the queue contains 0 tasks
