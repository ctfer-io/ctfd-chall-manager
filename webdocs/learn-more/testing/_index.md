---
title: Testing
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 5
description: >
    Learn how we test the plugin.
tags: [Testing, Security]
categories: [Explanations]
---

## Purpose 
Developing in an Open Source ecosystem is good, being active in responding to problems is better, detecting problems before they affect the end-user is the ideal goal!

Following this philosophy, we put a lot of effort into CI testing, mainly using [Cypress](https://www.cypress.io/), and analyze code security via [CodeQL](https://codeql.github.com/).

## GitHub Actions

From a technology point of view, we use GitHub Actions whenever possible to automate our tests. 

### Security

To ensure ongoing security, we enable advanced security analysis on the repository and conduct periodic scans with CodeQL on each pull request.

### Testing

Our tests are systematically executed on each push and pull request, following a two-stage process. 

The first stage involves Cypress for plugin integration, where we validate correct test cases to ensure comprehensive coverage. The second stage is executed to check for potential error with invalid cases. This stage runs after the Cypress tests to save time and due to technical constraints, such as the creation of challenges (preconditions).

To detect potential divergences with CTFd mode, we execute the tests in `mode: users` and `mode: teams`.

{{% imgproc testing.excalidraw Fit "800x800" %}}
{{% /imgproc %}}