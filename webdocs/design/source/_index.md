---
title: Source
github_repo: https://github.com/ctfer-io/ctfd-chall-manager
github_project_repo: https://github.com/ctfer-io/ctfd-chall-manager
weight: 3
description: >
    Learn how the *Source* abstraction is implemented in the plugin.
categories: [Explanations]
---

## Concept
As explained [here](/docs/chall-manager/glossary/#source), the *Source* refers to the team or user that initiates a request. This abstraction allows compatibility with CTFd operating in either “users” or “teams” mode, making the plugin versatile and usable in both modes.

To enable sharing across all users, the `sourceId` is set to `0`. The table below summarizes the different scenarios:

| user_mode | shared       | sourceId             |
|-----------|--------------|----------------------|
| users     | FALSE        | current_user.id      |
| teams     | FALSE        | current_user.team_id |
| users     | TRUE         | 0                    |
| teams     | TRUE         | 0                    |

## Example workflow
### Instance creation


Here an example of sourceId usage in the instance creation process:

```mermaid
flowchart LR
    A[Launch] --> B{CTFd mode}
    B -->|users| C[sourceId = user.id]
    B -->|teams| D[sourceId = user.team_id]
    D --> E{challenge.shared ?}
    C --> E
    E -->|True| F[sourceId = 0]
    E -->|False| End1
    F --> End1

    End1(((1)))

```

The rest of the workflows is detailed in [mana](/docs/ctfd-chall-manager/design/mana) section.
