---
title: Settings
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 1
description: >
    Manage the plugin settings.
tags: [Administration]
categories: [How-to Guides]
---

## Goal
This guide assumes you are a CTF administrator and you understand the key concepts. Before or during your event, you may need to configure or update the plugin. At the moment, you can configure the total amount of mana for Source or and the chall-manager API URL.

## Configure with environment variables

To configure the plugin at CTFd startup, you can use the next environment variables:

| Variable                      	| Default                      	| Description                                 	|
|-------------------------------	|------------------------------	|---------------------------------------------	|
| PLUGIN_SETTINGS_CM_API_URL    	| http://localhost:8080/api/v1 	| URL of Chall-Manager API                    	|
| PLUGIN_SETTINGS_CM_MANA_TOTAL 	| 0                            	| Maximum mana that source are allowed to use 	|

{{% alert title="Note" color="primary" %}}
The environment variable lookup is triggered at CTFd first startup. To modify settings, you need to change it on CTFd UI.
{{% /alert %}}

## Configure in UI

To configure or perform an update, Go to `CTFd Admin Panel` > `Plugins` > `chall-manager` > `Settings`, (1) select the text input, edit it, then (2) submit form, as shown below:

{{% imgproc setting-update Fit "800x800" %}}
{{% /imgproc %}}

{{% alert title="Warning" color="warning" %}}
We strongly recommends you to NOT edit the chall-manager API URL during your event.
{{% /alert %}}

## Additional environment variables

The plugin can optionally use 2 commons variables to configure cache or the logging level.

| Variable  	| Default 	| Description                                                                       	|
|-----------	|---------	|-----------------------------------------------------------------------------------	|
| REDIS_URL 	| ""      	| The URI to connect to a Redis server. (e.g. redis://user:password@localhost:6379) 	|
| LOG_LEVEL  	| "INFO"  	| Enumeration in INFO, DEBUG, ERROR, WARNING                                        	|