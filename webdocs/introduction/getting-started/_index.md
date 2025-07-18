---
title: Getting Started
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 3
description: |
  Create a challenge that deploys a Docker image and understand basic configuration.
resources:
  - src: "**.png"
  - src: "**gif"
tags: [Administration]
categories: [How-to Guides]
---

## Goal

In this tutorial, we will create a `dynamic_iac` challenge, a new challenge type introduced by the plugin. We will create a challenge where each player gets their own instance. We want an instance without mana cost, must be destroyed after 10 minutes without a maximum due date.

{{% alert title="Note" color="primary" %}}
If you are unfamiliar with the new attributes of the `dynamic_iac` challenge type, please refer to the related [design](/docs/ctfd-chall-manager/design). For guidance on maintenance operations (e.g., modifying challenge attributes), please refer to the relevant [guides](/docs/ctfd-chall-manager/guides). For details on the Infra-as-Code scenario, consult the appropriate [documentation](/docs/chall-manager/challmaker-guides).
{{% /alert %}}

## Prerequisites

This tutorial requires the installation of [Docker](https://docs.docker.com/engine/install/), [Docker Compose](https://docs.docker.com/compose/install/linux/), [Golang](https://go.dev/doc/install), and [ORAS](https://oras.land/docs/installation).

## Create the CTF Platform

Start all services with the registry:

```bash
cd hack
docker compose -f docker-compose-minimal.yml --profile registry up -d
```

Perform your CTFd setup at [http://localhost:8000/setup](http://localhost:8000/setup).

## Create the Challenge

### Create the Scenario and Push It to the Registry

For this example, your challenge will consist of 2 elements:
- The Docker image of your challenge (SSH server, web server, ...) that exposes 1 port.
- The [scenario](/docs/chall-manager/glossary/#scenario) that indicates to Chall-Manager how to deploy your challenge (the Docker image).

The scenario used is generic, which allows you to use this scenario and have any Docker image that exposes 1 port.

To build the scenario and push it to the local registry:

```bash
cd hack/docker-scenario
bash build.sh
```

{{% alert title="Note" color="primary" %}}
The scenario used here allows you to run a Docker container locally only. This is far from the actual capabilities of Chall-Manager. For more information, refer to the dedicated Chall-Manager [documentation](/docs/chall-manager).
{{% /alert %}}

### Create the Challenge on CTFd

We will follow the configuration presented in the [goal](#goal), which includes the following classic CTFd settings:

| Key                | Value       |
|--------------------|-------------|
| Name               | example     |
| Category           | example     |
| Message            | example     |
| Initial Value      | 500         |
| Decay Function     | Logarithmic |
| Decay              | 10          |
| Minimum Value      | 10          |

Since we want each player to have their own instance, disable the sharing option.

{{% imgproc create_challenge_sharing Fit "800x800" %}}
{{% /imgproc %}}

Next, disable the *Destroy on Flag*:

{{% imgproc create_challenge_destroy-on-flag Fit "800x800" %}}
{{% /imgproc %}}

Next, set the mana cost. You can leave it empty or configure an explicit 0.

{{% imgproc create_challenge_mana_cost_0 Fit "800x800" %}}
{{% /imgproc %}}

As mentioned, we want instances to be destroyed after 10 minutes of usage (600 seconds), without any due date:

Leave the *Until* value empty and configure the *Timeout* value at 600.

{{% imgproc create_challenge_until_timeout Fit "800x800" %}}
{{% /imgproc %}}

At the [previous step](#create-the-scenario-and-push-it-to-the-registry), we pushed the scenario to the registry `localhost:5000`. In Chall-Manager scope, you need to refer to the scenario by this name inside the Docker network.

{{% imgproc create_challenge_scenario Fit "800x800" %}}
{{% /imgproc %}}

Finally, click *Create* to set up the challenge.

{{% alert title="Note" color="primary" %}}
The first challenge creation can be long depending on your Internet connection. Chall-Manager will download the Pulumi plugin associated with the given scenario. Please be patient.
{{% /alert %}}

{{% imgproc create_challenge_create Fit "800x800" %}}
{{% /imgproc %}}

## Play the Challenge

Once the challenge has been created in CTFd and Chall-Manager, you can deploy **on-demand** instances of the scenario. To do this, go to the challenges page at [http://localhost:8000/challenges](http://localhost:8000/challenges).

{{% imgproc user_all Fit "800x800" %}}
{{% /imgproc %}}

To deploy the container, simply click on "Launch the challenge". A URL will be returned by the plugin, and the challenge will be accessible. You can verify that the image is correctly deployed on your computer:

```bash
docker ps | grep challenge
7b22cfa739ac 870ac2311d4b "/opt/CTFd/docker-en…" 22 seconds ago Up 21 seconds 0.0.0.0:32771->8000/tcp challenge-f953808a2ddbcace
```

To monitor instances directly from CTFd, go to the instance monitoring page at [http://localhost:8000/plugins/ctfd-chall-manager/admin/instances](http://localhost:8000/plugins/ctfd-chall-manager/admin/instances).

{{% imgproc admin_instance Fit "800x800" %}}
{{% /imgproc %}}

## Conclusion

In this guide, you have successfully set up a `dynamic_iac` challenge using the `CTFd-chall-manager` plugin. You learned how to create a CTF platform, build and push a scenario to a local registry, and configure a challenge on CTFd. You also explored how to deploy and manage instances of the challenge on demand.

By following these steps, you now have a functional challenge that allows each player to have their own instance, with specific mana costs and timeout settings. This setup leverages the capabilities of Chall-Manager to provide a dynamic environment for CTF challenges."

## What's Next

For further customization and advanced configurations, refer to the [design documentation](/docs/ctfd-chall-manager/design), [maintenance guides](/docs/ctfd-chall-manager/guides), and [ChallMaker documentation](/docs/chall-manager/challmaker-guides). These resources will help you deepen your understanding and optimize your challenge setup.
