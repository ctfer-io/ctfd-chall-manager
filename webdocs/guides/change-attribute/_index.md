---
title: Change challenge attributes
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 2
description: |
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

If you switch to a shared challenge mode, you need to deploy it from the panel. See the [associated documentation](docs/ctfd-chall-manager/guides/panel/#deploy-a-shared-instance).

Additionally, you will need to manually destroy instances that are no longer in use, or wait for them to be automatically deleted if a timeout or until condition has been configured.

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

This allows you to organize sales periods if you want to.

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
When you arrive on the modification page, you can see the current scenario reference.

{{% imgproc challenge-scenario Fit "800x800" %}}
{{% /imgproc %}}

By editing this value, you need to provide an update strategy.

{{% imgproc challenge-update-strategy Fit "800x800" %}}
{{% /imgproc %}}

The update can be long, depends on the update gap and the strategy.
