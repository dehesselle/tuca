# tool using Clouding.io API

This is an unofficial CLI tool that interacts with the Clouding.io's REST API. Its main goal is to provide a simple interface that I can use to create and destroy servers from shell scripts. Therefore it neither provides access to all available API endpoints nor to all available attributes and/or actions.

The project status is best described as "alpha" as things are still very much in motion and specifically tailored towards my usecase.

## Installation

`tuca` is on [PyPi](https://pypi.org/project/tuca/), you can use the package manager of your choice to set yourself up. Here is an example using `uv`:

```bash
uv tool install tuca
```

## Usage

### the basics

The CLI interface follows this pattern:

```bash
tuca <endpoint> <action> [options]
```

- `endpoint` is the same as in https://api.clouding.io/docs/
- `action` is one of `create`, `list` and `delete`
- `options` depend on `endpoint` and `action`, consult `--help` for details

`tuca` writes pretty-printed JSON (no colors) to `stdout`. It's both human-readable and intended to be piped into `jq` for non-interactive usage. The following example shows the available SSH keys (redacted values) in a freshly created account:

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

- always organized as list, even if the result count is 1 or 0
- usually named after the endpoint
- contains only a limited number attributes, but always `id` and `name`
- limited to 100 entries

### authentication

Before showing you examples, you need to setup an API token first. You can do that via environment variable:

```
export CLOUDINGIO_API_TOKEN=my_secret_token
```

Or, more securely, have tuca write it into your desktop's keyring. The following command will give you an interactive prompt to do that.

```
tuca auth create
```

_And before you say anything, I'm aware that `auth` is not an endpoint._

If you provide both, the environment variable takes precendence.

### here we go

Time to create your first server. First, pick an image.

```bash
tuca images list
```

<details>
<summary>Output</summary>

_(modified/shortened for brevity)_

```json
{
    "sizes/flavors": [
        ...
        {
            "accessMethods": {
                "password": "required",
                "sshKey": "not-supported"
            },
            "id": "jXEm7yK3MJ2VYkQ9",
            "minimumSizeGb": 25,
            "name": "Windows 11 (English 64Bit | Based on Windows Server 2025)"
        },
        ...
    ]
}
```
</details>

Now pick a size.

```bash
tuca flavors list
```

<details>
<summary>Output</summary>

_(modified/shortened for brevity)_

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

That's all to create a server with minimal configuration.

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
            "createdAt": "2026-02-04T23:42:16",
            "id": "mJOZBKqGP702Xjax",
            "name": "MyWinServer",
            "publicIp": null,
            "status": "Pending"
        }
    ]
}
```
</details>

Spooling up the server can take some time and you can check how it's doing.

```bash
tuca servers list --name MyWinServer
```
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