Feature: Workspace selection
  As a developer
  I want to select a project root folder
  So that AIHelm can execute git and AI commands in the correct workspace

  Background:
    Given an empty workspace repository

  Scenario: Select a workspace that contains .git
    Given a candidate directory "project_a" with .git
    When I select that directory as workspace
    Then the active workspace path is that directory
    And no git warning is required

  Scenario: Select a workspace without .git
    Given a candidate directory "project_b" without .git
    When I select that directory as workspace
    Then the active workspace path is that directory
    And a git warning is required

  Scenario: Workspace persists across restart
    Given a candidate directory "project_c" with .git
    When I select that directory as workspace
    And I restart workspace services from storage
    Then the active workspace path is that directory

  Scenario: Selecting a new workspace replaces active workspace
    Given a candidate directory "project_d" with .git
    And a candidate directory "project_e" with .git
    When I select "project_d" as workspace
    And I select "project_e" as workspace
    Then the active workspace path is "project_e"
