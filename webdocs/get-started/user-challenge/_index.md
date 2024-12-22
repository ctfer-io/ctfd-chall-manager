---
title: Play the challenge
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
description: >
  Visualize what the player will see during your CTF.
weight: 3
resources:
  - src: "**.png"
  - src: "**.gif"
categories: [How-to Guides]
---

## Goal 
In this tutorial we will see all actions a user has access to in order to control its instances.

## Prerequisites
At this step, we assume that you are a CTF player, the infrastructure is already configured and you understand the key concepts, if not please refer to associated [design](/docs/ctfd-chall-manager/design).

## Differents challenges mode

You can combine the values *Until* and *Timeout* to have 4 modes according to your needs:
* [None](#none)
* [Until](#until)
* [Timeout](#timeout)
* [Both](#both)

[Players](/docs/chall-manager/glossary/#player) can control all combinaisons, but each has these specificities.

{{% alert title="Note" color="primary" %}}
If the sharing option is enabled, only admins can launch the instance, see associated [guide](/docs/ctfd-chall-manager/guides/panel).
{{% /alert %}}

For all challenges, the default view (instance is not booted) will display a button to launch the instance, the mana cost and the remaining mana for current user.

{{% imgproc none_off Fit "800x800" %}}
{{% /imgproc %}}

To start the instance, click on the button.

{{% imgproc boot_instance Fit "800x800" %}}
{{% /imgproc %}}

### None
This mode allows you to use your instance with no duration limit.
Its deployment can cost you mana, but if you want to regain it, you need to destroy the instance.
If you want to reset your instance (either because it is soft-locked or you corrupted it), you can restart it.

{{% imgproc none_on Fit "800x800" %}}
{{% /imgproc %}}


### Until
This mode allows you to use the same actions as *None* mode, but the instance will be destroyed by the Janitor at a due date.
Don't worry, your mana will be automatically regained if the instance is janitored.

{{% imgproc until_on Fit "800x800" %}}
{{% /imgproc %}}

### Timeout
This mode allows you to use the same actions as *None* and *Until*, but the instance will be destroyed by the Janitor *n* seconds after their start.

{{% imgproc timeout_on Fit "800x800" %}}
{{% /imgproc %}}

If you see that the Janitor will destroy you instance soon, you can *renew* the instance (reset the timer).

{{% imgproc timeout_renew Fit "800x800" %}}
{{% /imgproc %}}

### Both 
With *Timeout* and *Until*, the plugin will display the timeout mode buttons, but Chall-Manager will take care of restricting or not the possibility of renewing the challenge based on the [design](/docs/chall-manager/design/expiration/).


## What's next ?
Congrat's ! If you've made it this far, you'll probably want to make a challenge for your event, and the plugin documentation doesn't include explanations on how to do this, so please refer to the associated [documentation](/docs/chall-manager/challmaker-guides/).

Otherwise, you can learn more about the plugin's design or advanced user guides here:
* [Learn the design](/docs/ctfd-chall-manager/design)
* [Use advanced guides](/docs/ctfd-chall-manager/guides)

