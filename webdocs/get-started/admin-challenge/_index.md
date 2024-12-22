---
title: Create a challenge
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 2
description: >
  Create a challenge and understand basic configuration.
resources:
- src: "**.png"
tags: [Administration]
categories: [How-to Guides]
---

## Goal

In this tutorial, we will create a `dynamic_iac` challenge, a new challenge type introduced by the plugin. <br>
If you are unfamiliar with the new attributes of the `dynamic_iac` challenge type, please refer to the related [design](/docs/ctfd-chall-manager/design). <br>
For guidance on maintenance operations (e.g., modifying challenge attributes), please refer to the relevant [guides](/docs/ctfd-chall-manager/guides).
For details on the Infra-as-Code scenario, consult the appropriate [documentation](/docs/chall-manager/challmaker-guides).

## Create the Challenge

For this example, we will create a challenge where each player gets their own instance. The instance will cost user 2 mana units, must be destroyed after 10 minutes without maximum due date, and using the scenario from the [no-sdk examples](https://github.com/ctfer-io/chall-manager/blob/main/examples/no-sdk).

Here are the basic CTFd settings:

| Key                	  | Value                    	  |
|---------------------	|------------------------   	|
| Name                	| example                   	|
| Category            	| example                    	|
| Message             	| example                   	|
| Initial Value       	| 500                       	|
| Decay Function      	| Logarithmic               	|
| Decay               	| 10                        	|
| Minimum Value         | 10                        	|

First, configure the scope. Since we want each player to have their own instance, disable the sharing option.

{{% imgproc create_challenge_sharing Fit "800x800" %}}
{{% /imgproc %}}

Next, let the *Destroy on Flag* disable

{{% imgproc create_challenge_destroy-on-flag Fit "800x800" %}}
{{% /imgproc %}}

Next, set the mana cost. Players will need to spend 2 mana to deploy their own instance of the challenge.

{{% imgproc create_challenge_mana_cost_2 Fit "800x800" %}}
{{% /imgproc %}}

As mentioned, we want instances to be destroyed after 10 minutes of usage (600 seconds), without any due date.

Let the *Until* value empty, and configure de *Timeout* value at 600.

{{% imgproc create_challenge_until_timeout Fit "800x800" %}}
{{% /imgproc %}}

Then, provide the scenario archive. For this example, we'll use `demo-deploy.zip` from the [no-sdk examples](https://github.com/ctfer-io/chall-manager/blob/main/examples/no-sdk).

Finally, click *Create* to set up the challenge.

{{% alert title="Note" color="primary" %}}
When you click Create, the upload process to the chall-manager may take several seconds. Please be patient.
{{% /alert %}}

{{% imgproc create_challenge_create Fit "800x800" %}}
{{% /imgproc %}}

## What's Next?

Congratulations! Your CTF installation is now configured to use the chall-manager for this challenge.

* [Play the challenge](/docs/ctfd-chall-manager/get-started/user-challenge)
* [Learn how it works](/docs/ctfd-chall-manager/design)
