---
title: Challenge
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 2
description: >
    Learn how we design the *dynamic_iac* challenge.
categories: [Explanations]
---

## Overview

The plugin introduces a new challenge type called `dynamic_iac`, allowing the deployment of instances per user or team (referred to as a source). It works seamlessly with both user modes defined by CTFd (individual users or teams).

## What’s new about this challenge type?

To get started, navigate to the challenge creation panel in CTFd and select the `dynamic_iac` challenge type.

{{% imgproc create_challenge_type Fit "800x800" %}}
{{% /imgproc %}}

Here’s what the plugin adds:

{{% imgproc create_challenge_attributes Fit "800x800" %}}
{{% /imgproc %}}

### Sharing

The **sharing** or **shared** is a boolean setting that allows a single instance to be shared among all players. 

For instance, in the following setup, challenges 1, 2, and 3 have the sharing enabled, while challenge 4 does not:

{{% imgproc pool_concept.excalidraw Fit "800x800" %}}
{{% /imgproc %}}

In this scenario, player X (yellow) and player Y (blue) will each have their own instances for challenge 4, but will share the same instance for challenges 1, 2, and 3. We recommend enabling this feature for static, stateless applications (e.g., websites).

### Destroy on flag

Challenges with the **destroy-on-flag** option will automatically destroy the instance when the player submits the correct flag. 

Please note: enabling this option will slow down CTFd's response time when the correct flag is submitted due to instance destruction. We recommend that you only activate this option if you don't want to use mana.

### Mana Cost

The **mana cost** is an integer representing the price users must pay in mana to deploy their own instance. Mana is refunded when the instance is destroyed. This system helps control the impact users have on the platform. For more details, see [how mana works](/docs/ctfd-chall-manager/desing/mana).


### Until

The **until** setting allows you to specify a date and time at which instances will be automatically destroyed by the Janitor.

**Example:**  
As a CTF administrator running a week-long event, you want a challenge available only on the first day. Set the Janitoring Strategy to **Until**, and configure the end date to DD/MM/YYYY 23:59. 

As a player, you can start your instance anytime before this date and destroy it whenever you like before the deadline.

### Timeout

The **timeout** is an integer that specifies, in seconds, how long after starting an instance the Janitor will automatically destroy it.

**Example:**  
As a CTF administrator or challenge creator, you estimate that your challenge takes about 30 minutes to solve. Set the Janitoring Strategy to **Timeout** and set the value to 1800 seconds (30 minutes).

As a player, once you start your instance, it will be destroyed after 30 minutes unless renewed. You can also manually destroy the instance at any time to reclaim your mana.

{{% alert title="Tips & Tricks" color="primary" %}}
You can either combine the *Until* and *Timeout* values or leave both undefined.
Find more info [here](/docs/chall-manager/design/expiration).
{{% /alert %}}

### Scenario Archive

The **scenario** is a zip archive defining the challenge deployment as a Golang Pulumi project. You can use [examples](https://github.com/ctfer-io/chall-manager/blob/main/examples) or create your own using the [SDK](/docs/chall-manager/design/software-development-kit/) and [Pulumi](https://pulumi.com).
