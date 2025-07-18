---
title: Configure the pooler
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 6
description: >
  Prepare your event or perform batch deployment.
resources:
- src: "**.png"
tags: [Administration]
categories: [How-to Guides]
---

## Goal 
Here, we assume that you are a CTF administrator, the infrastructure is already configured and you understand the key concepts.

## Purpose 
During your event, you may want to have a number of pre-deployed instances so that players can have an instance almost instantly.

Chall-Manager introduces the *Pooler* feature, which allows for a number of instances to be ready for use, significantly reducing the provisioning time for players. For more information, refer to the dedicated documentation on the [Pooler](/docs/chall-manager/design/pooler/)

## How to configure 

While your challenge creation or update, you can open the *Advanced* menu then go to *Pooler* section, and configure the *Min* and the *Max*. 

{{% imgproc pooler Fit "800x800" %}}
{{% /imgproc %}}