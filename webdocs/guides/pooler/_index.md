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
During your event, you may want to have a number of instances pre-deployed so that players can have an instance almost instantly.

In the case of a unique Docker image, the maximum time to plan for will be the time `t_x` that Chall-Manager takes to download the appropriate Pulumi plugin and the time `t_y` for the server on which your container will run to download this image, and finally, `t_z` the startup time of your image. The times `t_x` and `t_y` will be a few seconds and will only be felt during the first deployment of an instance. During the second deployment, Chall-Manager will already have these dependencies, and the server will already have the Docker image in cache, so only the time `t_z` will remain, which is unavoidable.

However, in the case of a more advanced scenario (e.g., creating a VM from scratch and configuring it via Ansible), the time `t_y` or `t_z` can take several minutes. And it is this time that we want to reduce.

The *Pooler*, introduced by Chall-Manager, addresses this issue. We can define a **minimum** number of instances to be deployed in the *Pool*. Instances in the *Pool* are not used by players, and when players request an instance, Chall-Manager draws from this *Pool* to ensure an instance is ready instantly. Using the *Pooler* eliminates the deployment time for players entirely.

While this time is eliminated for players, the infrastructure resource cost is still very real. Therefore, we can also configure a **maximum** in this Pool.

## How to configure 

While your challenge creation or update, you can open the *Advanced* menu then go to *Pooler* section, and configure the *Min* and the *Max*. 

{{% imgproc pooler Fit "800x800" %}}
{{% /imgproc %}}