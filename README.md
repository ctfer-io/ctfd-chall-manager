<div align="center">
<h1>CTFd-chall-manager</h1>
<p><b>Level Up CTFd with Infra-as-Code Challenges!</b><p>
<a href=""><img src="https://img.shields.io/github/license/ctfer-io/ctfd-chall-manager?style=for-the-badge" alt="License"></a>
<a href="https://github.com/ctfer-io/ctfd-chall-manager/actions?query=workflow%3Aci+"><img src="https://img.shields.io/github/actions/workflow/status/ctfer-io/ctfd-chall-manager/ci.yaml?style=for-the-badge&label=CI" alt="CI"></a>
<a href="https://github.com/ctfer-io/ctfd-chall-manager/actions/workflows/codeql-analysis.yaml"><img src="https://img.shields.io/github/actions/workflow/status/ctfer-io/ctfd-chall-manager/codeql-analysis.yaml?style=for-the-badge&label=CodeQL" alt="CodeQL"></a>
<a href="https://securityscorecards.dev/viewer/?uri=github.com/ctfer-io/ctfd-chall-manager"><img src="https://img.shields.io/ossf-scorecard/github.com/ctfer-io/ctfd-chall-manager?label=openssf%20scorecard&style=for-the-badge" alt="OpenSSF Scoreboard"></a>
</div>

> [!CAUTION]
> CTFd-chall-Manager is currently in public beta phase.
> It could be run in production, but breaking changes are subject to happen in the upcoming months until General Availability.
> 
> It has been tested under production workload during the NoBrackets 2024.

This plugin allow you to use the [chall-manager](https://github.com/ctfer-io/chall-manager), to manage scenario and permit Player's to deploy their instances.

Last version tested on: [3.7.5](https://github.com/CTFd/CTFd/releases/tag/3.7.5).

# Features
## Main features for Users
- Booting/Destroying Instance by Source
- Sharing Instance between all Sources
- Restriction based on Mana
- Use flag variation proposed by [chall-manager](https://github.com/ctfer-io/chall-manager)

<img style="width: 90%; display: block; margin: auto; box-sizing: border-box;" src="res/boot_instance.gif"/>

## Main features for Admins
- Create challenges with Scenario
- Preprovisionng Instances for Source
- Monitor all mana used by Sources

<img style="width: 90%; display: block; margin: auto; box-sizing: border-box;" src="res/flags.png"/>

# How install and use
To install and use the plugin, refer to the documentation at https://ctfer.io/docs/ctfd-chall-manager.

# Limitations
- Need to use the `core-beta` theme (cf https://github.com/CTFd/CTFd/pull/2630)

# Glossaries

| Label    | Description                                                                                 |
|----------|---------------------------------------------------------------------------------------------|
| Sources  | In CTFd "Teams" mode, the Source is Team <br>In CTFd "Users" mode, the Source is User       |
| Scenario | Pulumi project that define the challenge (webserver, ssh server, ...) to deploy an Instance |
| Instances| This is a copy of Scenario for the Source that make the request                             |
| Mana     | This is the "money" to regulate the Instance's deployment                                   |

