---
title: Architecture
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 1
description: >
    Learn how we design the plugin.
tags: [Architecture]
categories: [Explanations]
---

## Concept

As explained in the chall-manager [documentation](/docs/chall-manager), we avoid exposing its API to prevent the risk of direct resource manipulation by players. 

CTFd inherently provides functionalities like authentication, team management, scoring, and flag handling. By adding our plugin, CTFd can serve as both a challenge management platform for administrators and a request manager that acts as a proxy with user authentication, mana limitations, and more.

## Overview

The basic architecture is straightforward: we have created new API endpoints for both administrators and users. These endpoints mainly handle CRUD operations on challenge instances.

{{% imgproc architecture-plugin-overview.excalidraw Fit "800x800" %}}
{{% /imgproc %}}

## API

### AdminInstance

This endpoint allows administrators to perform CRUD operations on *challengeId* for a specified *sourceId*. Essentially, this endpoint forwards requests to the chall-manager for processing.

### UserInstance

Unlike the AdminInstance endpoint, this one does not accept *sourceId* as a parameter. Instead, it automatically identifies the source issuing the request and checks mana availability before forwarding the request to the chall-manager.

### UserMana

This endpoint handles GET requests to display the remaining mana of the source issuing the request.

## Detailed Overview

The following diagram provides a more detailed view of how your browser interacts with the API endpoints and how these endpoints are mapped to the corresponding chall-manager endpoints.

{{% imgproc architecture-plugin.excalidraw Fit "800x800" %}}
{{% /imgproc %}}

