---
title: Why the plugin exists
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
description: >
A quick introduction to what CTFd-chall-manager is and why it should be used.
weight: 1
resources:
- src: "**.png"
- src: "**.gif"
categories: [How-to Guides]
---

## Why Chall-Manager exists?

Originally, [CTFer.io](https://ctfer.io) used Pulumi in Go to deploy CTFd in a Kubernetes cluster due to our software development expertise. One of Chall-Manager's target capabilities was "anything deployable by Pulumi could be managed by Chall-Manager." This promise would have been difficult to achieve if we used only Python, as it required many dependencies and would force each plugin user to rebuild the CTFd Docker image.

Additionally, we aimed for an Offline-First model, and using Golang made it easier to achieve this goal because we could compile the program and deploy it in a Docker image.

However, executing Pulumi with Go inside CTFd was not possible, so we had to create a dedicated system.

In summary, each component has its own scope:
- Chall-Manager: Exposed an API to manage challenges using infrastructure-as-code.
- CTFd: Handled player authentication, the scoreboard, challenges, and the web interface.
- CTFd-chall-manager: Acted as the bridge between the two components.

## How CTFd-chall-manager works with CTFd and Chall-Manager?

CTFd-chall-manager is a CTFd plugin designed to enhance CTFd's core functionalities. Chall-Manager allowed the execution of any Pulumi project as long as it adhered to the syntax required by the SDK.

The CTFd-chall-manager plugin served as a user interface for the Chall-Manager system, making it accessible and user-friendly for a broader audience. The plugin exposed an API within CTFd, performing necessary checks before forwarding requests to Chall-Manager.