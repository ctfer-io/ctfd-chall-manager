---
title: Setup
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 1
description: >
  Learn how to install the plugin in your CTFd.
resources:
- src: "**.png"
tags: [Setup, Infrastructure]
categories: [How-to Guides]
---

## Goal
This tutorial will guide you through the installation and configuration of the CTFd-chall-manager plugin to use [chall-manager](https://github.com/ctfer-io/chall-manager).

## Prerequisites
Ensure you have chall-manager running before starting this tutorial. You can find the relevant [documentation](/docs/chall-manager) for setup instructions.

## Install the plugin
If you are not using the `docker-compose.yml` file, you need to clone the repository into `CTFd/CTFd/plugins/ctfd-chall-manager`.

{{< tabpane >}}
  {{< tab header="Bash" lang="Bash" >}}
# Clone the CTFd repository
git clone https://github.com/CTFd/CTFd

# Clone the plugin repository
git clone https://github.com/ctfer-io/ctfd-chall-manager CTFd/CTFd/plugins/ctfd-chall-manager

# (optional) Start Redis with Docker
docker run -d -p 6379:6379 redis:<version>

## (optional) Configure plugin to use redis serveur
export REDIS_URL=redis://localhost:6379

# Start CTFd
cd CTFd
python3 -m venv venv 
source venv/bin/activate 
pip3 install -r requirements.txt
python3 serve.py 
  {{< /tab >}}
  {{< tab header="Docker" lang="Bash" >}}
# Clone the plugin repository
git clone https://github.com/ctfer-io/ctfd-chall-manager

# Create Docker network
docker network create testing

# (optional) Start Redis with Docker
docker run -d --name redis-svc --network testing redis:<version>

# Start CTFd with Docker
docker run -d -p 8000:8000 [-e REDIS_URL=redis://redis-svc:6379] -v ./ctfd-chall-manager:/opt/CTFd/CTFd/plugins/ctfd-chall-manager --network testing ctfd/ctfd:<version>
  {{< /tab >}}
{{< /tabpane >}}

{{% alert title="Tips & Tricks" color="primary" %}}
You can use assets in GitHub releases instead of cloning the whole repository: https://github.com/ctfer-io/ctfd-chall-manager/releases 
{{% /alert %}}

After completing this step, you should be able to access the plugin settings configuration in the CTFd UI.

{{% imgproc install_check_ui Fit "800x800" %}}
The plugin is visible in the UI
{{% /imgproc %}}

If the plugin does not appear, verify your container volume mounts, then check the CTFd logs for import module entries, such as:

{{% imgproc install_check_logs Fit "800x800" %}}
The plugin is visible in the logs
{{% /imgproc %}}

## Configure the plugin to use chall-manager

To connect the plugin to chall-manager, go to the plugin settings.

The default configuration is:

{{% imgproc settings_default Fit "800x800" %}}
Default plugin configuration
{{% /imgproc %}}

Adjust the plugin settings to match your environment, ensuring CTFd can communicate with chall-manager. For instance:

{{% imgproc settings_configured Fit "800x800" %}}
CTFd can successfully reach chall-manager
{{% /imgproc %}}

## What's next?
Congratulations! At this point, your setup is ready to use chall-manager for your CTF events.
* [Create a challenge](/docs/ctfd-chall-manager/get-started/admin-challenge)
