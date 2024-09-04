---
title: Challenge
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 2
description: >
    Manage your dynamic_iac challenge.
tags: [Administration]
categories: [How-to Guides]
---

## Goal 
Here, we assume that you are a CTF administrator, the infrastructure is already configured and you understand the key concepts.
During or before your event you may need to change challenge attributes.

For all updates, go to the CTFd Admin Panel and edit the challenge (https://CTFD_URL/admin/challenges).

{{% imgproc admin-challenge Fit "800x800" %}}
{{% /imgproc %}}


## Change the global scope
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-scope Fit "800x800" %}}
{{% /imgproc %}}

By editing this value, you trigger instances destruction, see workflow belows:

```mermaid
flowchart LR
    A[Update] --> B
    B[Update on CTFd backend] --> C 
    C{challenge global ?} 
    C -->|True|F[Destroy all instances]
    C -->|False| E[Destroy global instance] 
    E --> H[Send update payload to CM]
    F --> H
```

## Change the mana cost
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-mana Fit "800x800" %}}
{{% /imgproc %}}

By editing this value, you do not edit the existing coupons of this challenge. 
Also, you can organize sales periods.

## Change the janitoring strategy
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-janitoring Fit "800x800" %}}
{{% /imgproc %}}

{{% alert title="Warning" color="warning" %}}
You can edit this value, but you can't change into None value due to CM limitation at this moment.
An issue is open and work in progress.
{{% /alert %}}


## Change the scenario
When you arrive on the modification page, you can download the current scenario archive.

{{% imgproc challenge-scenario Fit "800x800" %}}
{{% /imgproc %}}

By editing this value, you need to provide an update strategy.

{{% imgproc challenge-update-strategy Fit "800x800" %}}
{{% /imgproc %}}

The update can be long, depends on the update gap and the strategy.

## FAQ