<div align="center">
<h1>CTFd-chall-manager</h1>
<p><b>Level Up CTFd with Infra-as-Code Challenges!</b><p>
<a href=""><img src="https://img.shields.io/github/license/ctfer-io/ctfd-chall-manager?style=for-the-badge" alt="License"></a>
<a href="https://github.com/ctfer-io/ctfd-chall-manager/actions?query=workflow%3Aci+"><img src="https://img.shields.io/github/actions/workflow/status/ctfer-io/ctfd-chall-manager/ci.yml?style=for-the-badge&label=CI" alt="CI"></a>
	<a href="https://github.com/ctfer-io/ctfd-chall-manager/actions/workflows/codeql-analysis.yml"><img src="https://img.shields.io/github/actions/workflow/status/ctfer-io/ctfd-chall-manager/codeql-analysis.yml?style=for-the-badge&label=CodeQL" alt="CodeQL"></a>
</div>

This plugin allow you to use the [chall-manager](https://github.com/ctfer-io/chall-manager), to manage scenario and permit Player's to deploy their instances.

# Features
## Main features for Users
- Booting/Destroying Instance by Source
- Sharing Instance between all Sources
- Restriction based on Mana
- Use flag variation proposed by [chall-manager](https://github.com/ctfer-io/chall-manager)

<img style="width: 90%; display: block; margin: auto; box-sizing: border-box;" src="./img/boot_instance.gif"/>

## Main features for Admins
- Create challenges with Scenario
- Preprovisionng Instances for Source
- Monitor all mana used by Sources

<img style="width: 90%; display: block; margin: auto; box-sizing: border-box;" src="./img/flags.png"/>

# How install and use
To install the plugin, you need to clone the repository in `CTFd/plugins` folders. <br>
To use the plugin, refer to the documentation at https://ctfer.io/docs#ctfd-chall-manager .

# Glossaries

| Label    | Description                                                                                 |
|----------|---------------------------------------------------------------------------------------------|
| Sources  | In CTFd "Teams" mode, the Source is Team <br>In CTFd "Users" mode, the Source is User       |
| Scenario | Pulumi project that define the challenge (webserver, ssh server, ...) to deploy an Instance |
| Instances| This is a copy of Scenario for the Source that make the request                             |
| Mana     | This is the "money" to regulate the Instance's deployment                                   |

