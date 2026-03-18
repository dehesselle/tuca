<!--
SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>

SPDX-License-Identifier: GPL-2.0-or-later
-->

# tool using Clouding.io API

This is an unofficial CLI that interacts with Clouding.io's REST API. Its main purpose is to provide a simple interface to create and destroy servers from snapshots/images. It is not an all-encompassing tool as it neither provides access to all API endpoints nor all actions.

The project status is best described as "alpha" as things are still very much in motion.

## Installation

`tuca` is on [PyPi](https://pypi.org/project/tuca/), use the package manager of your choice to set yourself up. Here is an example using `uv`:

```bash
uv tool install tuca
```

## Usage

### The basics

The CLI interface follows this pattern:

```bash
tuca <endpoint> <action> [options]
```

- `endpoint` is the same as in the [API documentation](https://api.clouding.io/docs/)  
  💁 _Not all endpoints are supported!_
- `action` is one of `create`, `list` and `delete`  
  💁 _Supported actions depend on endpoint!_
- `options` depend on `endpoint` and `action`  
  💁 _Consult `--help` for details!_

`tuca` writes pretty-printed JSON (no colors) to `stdout`. It's human-readable and can be piped into `jq` for non-interactive usage. The following example shows the output from `list`ing the `keypairs` endpoint (values redacted):

```json
{
    "keypairs": [
        {
            "fingerprint": "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00",
            "id": "xxxxxxxxxxxxxxxx",
            "name": "default"
        }
    ]
}
```

The output is

- always presented as list, even if the result count is 1 or 0
- usually named after the endpoint
- contains an opionated subset of the available attributes, but always `id` and `name`
- limited to a maximum of 100 entries

### Setup authentication

First order of business is setting up an API token. You can do that via environment variable:

```bash
export CLOUDINGIO_API_TOKEN=my_secret_token
```

Or, more securely, have tuca write it into your system's keyring. The following command will give you an interactive prompt to do that:

```bash
tuca auth create
```

If credentials are present in both keyring and environment, the environment variable takes precedence.

### Create a server

Pick one of the available Windows images.

```bash
tuca images list --filter windows
```

<details>
<summary>Output</summary>

```json
{
    "images": [
        {
            "accessMethods": {
                "password": "required",
                "sshKey": "not-supported"
            },
            "id": "Lka79zd4JDnxyr85",
            "minimumSizeGb": 25,
            "name": "Windows Server 2022 Datacenter (English 64Bit)"
        },
        {
            "accessMethods": {
                "password": "required",
                "sshKey": "not-supported"
            },
            "id": "jG4bZNnEQznYx7LP",
            "minimumSizeGb": 25,
            "name": "Windows Server 2016 Datacenter (English 64Bit) EOL"
        },
        {
            "accessMethods": {
                "password": "required",
                "sshKey": "not-supported"
            },
            "id": "WwQ6kDdVqb2Jeaml",
            "minimumSizeGb": 25,
            "name": "Windows Server 2019 Datacenter (English 64Bit) EOL"
        },
        {
            "accessMethods": {
                "password": "required",
                "sshKey": "not-supported"
            },
            "id": "kbxmpG2bXvKwlaDg",
            "minimumSizeGb": 25,
            "name": "Windows Server 2025 Datacenter (English 64Bit)"
        },
        {
            "accessMethods": {
                "password": "required",
                "sshKey": "not-supported"
            },
            "id": "jXEm7yK3MJ2VYkQ9",
            "minimumSizeGb": 25,
            "name": "Windows 11 (English 64Bit | Based on Windows Server 2025)"
        },
        {
            "accessMethods": {
                "password": "required",
                "sshKey": "not-supported"
            },
            "id": "q58XEgdA0P26mA0j",
            "minimumSizeGb": 25,
            "name": "Windows 11 (Espa\u00f1ol 64Bit | Basado en Windows Server 2025)"
        }
    ]
}
```

</details>

Now pick one of the available flavors (server sizes).

```bash
tuca flavors list
```

<details>
<summary>Output</summary>

_(output shortened)_

```json
{
    "sizes/flavors": [
        ...
        {
            "id": "8x16",
            "pricePerHour": 0.05472,
            "pricePerMonthApprox": 39.9456,
            "ramGb": 16,
            "vCores": 8.0
        },
        ...
    ]
}
```

</details>

That's sufficient to create a server with minimal configuration.

```bash
# Windows 11 compatible image
# 8 cores, 16 GB RAM
# default firewall
# default image size
tuca servers create --image jXEm7yK3MJ2VYkQ9 --name MyWinServer --flavorid 8x16 --password start123
```

<details>
<summary>Output</summary>

```json
{
    "servers": [
        {
            "action": {
                "completedAt": null,
                "id": "BEVPodeblJYKJv7a",
                "resourceId": "R0XZEKlWEAMdWbQj",
                "resourceType": "server",
                "startedAt": "2026-02-28T14:38:52.312803Z",
                "status": "inProgress",
                "type": "create"
            },
            "createdAt": "",
            "id": "R0XZEKlWEAMdWbQj",
            "name": "MyWinServer",
            "publicIp": "",
            "status": "Pending"
        }
    ]
}
```

</details>

Creating the server can take some time and you can check how it's doing.

```bash
tuca servers list --name MyWinServer
```

<details>
<summary>Output</summary>

```json
{
    "servers": [
        {
            "createdAt": "2026-02-28T14:38:52",
            "id": "R0XZEKlWEAMdWbQj",
            "name": "MyWinServer",
            "publicIp": null,
            "status": "Creating"
        }
    ]
}
```

</details>

The server will be ready eventually.

<details>
<summary>Output</summary>

```json
{
    "servers": [
        {
            "createdAt": "2026-02-04T23:42:16",
            "id": "mJOZBKqGP702Xjax",
            "name": "MyWinServer",
            "publicIp": "103.23.60.115",
            "status": "Active"
        }
    ]
}
```

</details>

## License

[GPL-2.0-or-later](https://github.com/dehesselle/tuca/blob/main/LICENSE)
