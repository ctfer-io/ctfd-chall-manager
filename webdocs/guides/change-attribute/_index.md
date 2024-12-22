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


## Change the scope
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-sharing Fit "800x800" %}}
{{% /imgproc %}}

By editing this value, you trigger instances destruction, see workflow belows:

```mermaid
flowchart LR
    A[Update] --> B
    B[Update on CTFd backend] --> C 
    C{challenge is shared ?} 
    C -->|True|F[Destroy all instances]
    C -->|False| E[Destroy the shared instance] 
    E --> H[Send update payload to CM]
    F --> H
```

## Change the destroy on flag 
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-destroy-on-flag Fit "800x800" %}}
{{% /imgproc %}}

You can edit this value at any time without any impact on Chall-Manager API.

## Change the mana cost
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-mana Fit "800x800" %}}
{{% /imgproc %}}

By editing this value, you do not edit the existing coupons of this challenge. 
Also, you can organize sales periods.

## Change Timeout 
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-timeout Fit "800x800" %}}
{{% /imgproc %}}

You can change or reset this value, Chall-Manager will update all the computed `until` for instances. 

## Change Until 
When you arrive on the modification page, the value displayed is the one configured at the challenge level.

{{% imgproc challenge-until Fit "800x800" %}}
{{% /imgproc %}}

You can change or reset this value, Chall-Manager will update all the computed `until` for instances. 

## Change the scenario
When you arrive on the modification page, you can download the current scenario archive.

{{% imgproc challenge-scenario Fit "800x800" %}}
{{% /imgproc %}}

By editing this value, you need to provide an update strategy.

{{% imgproc challenge-update-strategy Fit "800x800" %}}
{{% /imgproc %}}

The update can be long, depends on the update gap and the strategy.
