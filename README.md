<div align="center">

# fireprox-ng

fireprox-ng is a refresh of the widely loved fireprox.

<br>

[Why](#why) •
[Installation](#installation) •
[Getting started](#getting-started) •
[Usage](#usage) •
[Coming Soon](#coming-soon) •
[Thanks](#thanks)

</div><br>

# Why

The original fireprox project appears to be umaintained and I assume most organizations have transitioned to maintaining an internal version of the tool. We need fireprox to enable continuous penetration testing and would like to open up the updated version of the tool to the public.

</div>
<br>

## Installation

fireprox-ng be installed from the PyPi using the following command:

```
pipx install fireproxng
```

If this tool is not yet availible via PyPi, you can install it directly from the repository using:

```
pipx install git+https://github.com/puzzlepeaches/fireproxng.git
```

For development, clone the repository and install it locally using Poetry.

```
git clone https://github.com/puzzlepeaches/fireproxng.git
cd fireproxng
poetry shell && poetry install
```

<br>

## Getting started

fireprox-ng holds the same functionality as its predecessor, fireprox. The utility now however has been moderized to be more user friendly with argument driven operations along with a more intuitive interface.

fireprox-ng has four subcommands:

- create
- delete
- list
- update

All functionality is shared with the original tool. fireprox-ng can be called using `fireprox-ng` or `fpng`.

<br>

## Usage

The help menu for the base utility is shown below:

```
 Usage: fpng [OPTIONS] COMMAND [ARGS]...

 fireprox-ng is a tool for deploying AWS API Gateway proxies.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help  -h  Show this message and exit.                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ create                  Create a new fireprox-ng proxy.                                                                       │
│ delete                  Delete a fireprox-ng proxy.                                                                           │
│ list                    List all fireprox-ng proxies.                                                                         │
│ update                  Update a fireproxy-ng proxy.                                                                          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

All subcommands expect AWS credentials sourced from command line parameters, environment variables, or the aws credentials file (perfered). Major regions are supported.

```
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --access_key         -ak                                                                                                      │
│ --secret_access_key  -sk                                                                                                      │
│ --session_token      -st                                                                                                      │
│ --region             -r                                                                                                       │
│ --help               -h   Show this message and exit.                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

The environment variables fireprox-ng can read from are as follows:

- access_key - AWS_ACCESS_KEY_ID
- secret_access_key - AWS_SECRET_ACCESS_KEY
- region - AWS_REGION

<br>

### Create

An example help menu for the create subcommand is shown below:

```
 Usage: fpng create [OPTIONS] [PROFILE_NAME] [TARGET]...
```

By default the tool will read from the credentials file default profile. If you wish to use a different profile, you can specify it using the `profile_name` subcommand. When creating a new proxy endpoint, you can specify an arbitrary number of URLs to stage the API gateway. The tool will automatically generate a unique name for the proxy endpoint. For example you can do the following:

```
fpng create https://example.com https://example.com/api/v1 https://example.com/api/v2
```

This will stage multiple endpoints with the same name and different api-id values.

<br>

### Delete

The same goes as above for the delete subcommand with the fireprox-ng enhanced capability to delete multiple endpoints at once. The help menu for the delete subcommand is shown below:

```
 Usage: fpng delete [OPTIONS] [PROFILE_NAME] [API_ID]...
```

An example of the delete command in action is shown below:

```
fpng delete lvofzv6sc2 n7sark2eei
```

You can alternatively specify "all" as the API ID to delete all endpoints.

```
fpng delete all
```

<br>

### List

fireprox-ng can also list existing API endpoints not in a deleted state. The help menu for the list subcommand is shown below:

```
 Usage: fpng list [OPTIONS] [PROFILE_NAME]
```

An example command to list all endpoints is shown below:

```
fpng list
```

<br>

### Update

The update subcommand includes the ability to update the target of an existing endpoint using an API ID. The help menu for the update subcommand is shown below:

```
 Usage: fpng update [OPTIONS] [PROFILE_NAME] API_ID TARGET
```

<br>

## Coming Soon

Some planned features coming in the next release:

- Better credential handling (AWS is annoying)
- Create proxy endpoints across multiple regions
- Update fireprox-ng endpoint name when updating target
- Alternate service usage for proxying traffic
- Session token handling (This is borken currently and I don't know anyone who uses it)
- Default URL set staging config files
- YAML config file support

<br>

## Thanks

- The original [fireprox](https://github.com/ustayready/fireprox) of course from ustayready.
