---
title: Quickstart
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 2
description: >
  A short guide on setting up a simple CTFd with Chall-Manager setup locally with Docker.
resources:
- src: "**.png"
tags: [Setup, Infrastructure]
categories: [How-to Guides]
---


## Goal

In this tutorial, you will deploy a test environment containing [Chall-Manager](https://github.com/ctfer-io/chall-manager), [CTFd](https://github.com/CTFd/CTFd), and the [CTFd-chall-manager](https://github.com/ctfer-io/ctfd-chall-manager) plugin.

### Local Docker

#### Prerequisites

This tutorial requires the installation of [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/linux/).

#### Create CTF Platform

##### Step 1 - Start the Services

{{% alert title="Note" color="primary" %}}
The `docker-compose.yml` file **should not be used in production as is** because the architecture is not secure by default (certificates, HA, passwords, etc.). This installation will serve as an example in this tutorial and will give you a working base to get started with the plugin without a heavy production installation.
For a "prod-ready" installation, refer to the following tools: [ctfer](https://github.com/ctfer-io/ctfer) or [fullchain](https://github.com/ctfer-io/fullchain).
{{% /alert %}}

```bash
cd hack
docker compose -f docker-compose-minimal.yml up -d
```

##### Step 2 - Check All Services

Perform the CTFd configuration, then go to the plugin UI.

- Admin Panel > Plugins > Chall-Manager

{{% imgproc install_check_ui Fit "800x800" %}}
{{% /imgproc %}}

The **Status** should be **reachable**. If not, check your installation and the containers running on your machine; there might be a conflict.

{{% imgproc settings_configured Fit "800x800" %}}
CTFd can successfully reach Chall-Manager.
{{% /imgproc %}}

#### Destroy CTF Platform

When you are done, remove the CTF platform:

```bash
cd hack
docker compose -f docker-compose-minimal.yml down -v
```