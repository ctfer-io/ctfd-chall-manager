---
title: Panel
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 3
description: >
  Prepare your event or perform batch deployment.
resources:
- src: "**.png"
tags: [Administration]
categories: [How-to Guides]
---

## Goal 
Here, we assume that you are a CTF administrator, the infrastructure is already configured and you understand the key concepts.

During your event you may need to deploy instances for users we will see several use cases.
If mana is enabled, 1 coupon will be created for each user.

{{% alert title="Note" color="primary" %}}
Even if users don't have the required mana, the instance will be created here.
{{% /alert %}}


## Deploy instances for users

There may be several reasons why administrators create instances for users. 
Here, we'll imagine that the CTF hasn't started yet, that it's a CTF in team mode and that 10 teams are expected. For the 10 teams, we want to deploy 1 instance of a challenge.

Go to `CTFd Admin Panel` > `Plugins` > `chall-manager` > `Panel` such as:

{{% imgproc batch-deploy Fit "800x800" %}}
{{% /imgproc %}}

By clicking on the button, you will send several requests to CTFd.
To make the user experience easier, we add a progress bar.

{{% imgproc panel-deploy Fit "800x800" %}}
{{% /imgproc %}}

Once the progress bar is done (this mean instances are created on chall-manager), you can go the instances monitoring panel.

{{% imgproc instance-monitoring Fit "800x800" %}}
{{% /imgproc %}}

You can use this method during your event to deploy a hidden challenge (deploy instances before the challenge is release) for instance.

## Deploy a shared instance

Here, we'll imagine that you did configure a challenge with the sharing option enabled.
For a shared challenge, you must put the pattern at **0**, or leave it empty.

{{% imgproc panel-shared Fit "800x800" %}}
{{% /imgproc %}}

Like the previous use case, you will get a progress bar while the instance are getting deployed.




