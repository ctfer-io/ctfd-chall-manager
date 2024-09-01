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

### Testing

Our test sheets are executed at each push and pull request, and the test sheets evolve according to the features added by the plugin. 

### Security

To ensure ongoing security, we enable advanced security analysis on the repository and conduct periodic scans with CodeQL on each pull request.

