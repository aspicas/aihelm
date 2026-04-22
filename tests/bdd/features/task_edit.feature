Feature: Task Editing
  As a developer
  I want to edit queued tasks
  So that I can refine instructions before they are executed

  Background:
    Given an empty task queue

  Scenario: Edit the name of a queued task
    When I add a task with name "Original" prompt "do stuff" and branch "feature/orig"
    And I edit the task name to "Updated"
    Then the task has name "Updated"
    And the task prompt is "do stuff"

  Scenario: Edit the prompt of a queued task
    When I add a task with name "T" prompt "Old prompt" and branch "feature/t"
    And I edit the task prompt to "New prompt"
    Then the task prompt is "New prompt"

  Scenario: Edit the branch of a queued task
    When I add a task with name "T" prompt "p" and branch "feature/old"
    And I edit the task branch to "feature/new"
    Then the task has branch "feature/new"

  Scenario: Reject editing a running task
    Given a running task with name "T" prompt "p" and branch "feature/run"
    When I try to edit the task name to "New"
    Then I receive a validation error containing "Only queued tasks can be edited"

  Scenario: Reject duplicate branch on edit
    When I add a task with name "A" prompt "p" and branch "feature/a"
    And I add a task with name "B" prompt "p" and branch "feature/b"
    And I try to edit task "B" branch to "feature/a"
    Then I receive a validation error containing "already assigned"

  Scenario: Edited task persists
    Given a JSON-backed task queue
    When I add a task with name "Before" prompt "p" and branch "feature/persist"
    And I edit the task name to "After"
    And I reload the queue from storage
    Then the task has name "After"
