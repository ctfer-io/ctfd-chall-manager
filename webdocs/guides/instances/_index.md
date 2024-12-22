---
title: Instances
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 4
description: >
    Monitor and Manage instances.
tags: [Administration]
categories: [How-to Guides]
---

## Goal
This guide assumes you are a CTF administrator with a properly configured infrastructure and an understanding of key concepts.

During your event, you may need to monitor or manage instances associated with Sources.

## How to do it
### Monitoring
To monitor instances, go to the plugin settings in the `CTFd Admin Panel` > `Plugins` > `chall-manager` > `Instances` section.

{{% imgproc instances-monitoring Fit "800x800" %}}
{{% /imgproc %}}

### Administration
You can *Renew* , *Restart* or *Destroy* an individual instance by clicking the corresponding button in the instance row.

To perform actions on multiple instances, (1) select the instances using the checkboxes, (2) click the associated button, (3) then confirm your choice, as shown below:

{{% imgproc instances-batch-delete Fit "800x800" %}}
{{% /imgproc %}}
