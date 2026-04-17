Feature: Task Queue Management
  As a developer
  I want to add tasks with specific branch names to a waiting list
  So that the AI can work sequentially without my constant intervention

  Background:
    Given an empty task queue

  Scenario: Add a valid task to the queue
    When I add a task with name "Fix login" prompt "Refactor auth module" and branch "feature/fix-login"
    Then the queue contains 1 task
    And the task has status "queued"
    And the task has branch "feature/fix-login"

  Scenario: Reject task with invalid branch name
    When I try to add a task with name "Bad" prompt "p" and branch "feature/bad name"
    Then I receive a validation error containing "Invalid git branch name"

  Scenario: Reject task with empty name
    When I try to add a task with an empty name
    Then I receive a validation error containing "name"

  Scenario: Reject duplicate active branch
    Given a queued task with branch "feature/existing"
    When I try to add a task with name "Dup" prompt "p" and branch "feature/existing"
    Then I receive a validation error containing "already assigned"

  Scenario: Tasks are ordered by position
    When I add a task with name "First" prompt "p1" and branch "feature/first"
    And I add a task with name "Second" prompt "p2" and branch "feature/second"
    Then the queue lists "First" before "Second"

  Scenario: Tasks persist across restarts
    Given a JSON-backed task queue
    When I add a task with name "Persistent" prompt "p" and branch "feature/persist"
    And I reload the queue from storage
    Then the queue contains 1 task
    And the task has name "Persistent"
