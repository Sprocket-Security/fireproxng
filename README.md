<div align="center">

# fireproxng

fireproxng is a refresh of the widely loved fireprox.

<br>

[Why](#why) •
[Installation](#installation) •
[Getting started](#getting-started) •
[Usage](#usage) •
[Example Usage](#example-usage) •
[Coming Soon](#coming-soon) •
[Thanks](#thanks)

#### Check out the [Sprocket Security Blog]([https://sprocketsecurity.com/resources/](https://www.sprocketsecurity.com/resources/evading-external-network-security-controls)) for more details!

</div><br>

</div>

# Why

The original fireprox project appears to be mostly unchanged and I assume most organizations have transitioned to maintaining an internal version of the tool. We need fireprox to enable continuous penetration testing and would like to open up the updated version of the tool to the public.

fireproxng also includes some evasion features that are not present in the original fireprox. Please see the [Thanks](#thanks) section for more information.

<br>

## Installation

fireproxng be installed from the PyPi using the following command:

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

fireproxng holds the same functionality as its predecessor, fireprox. The utility now however has been moderized to be more user friendly with argument driven operations along with a more intuitive interface.

fireproxng has four subcommands:

- create
- delete
- list
- update

All functionality is shared with the original tool. fireproxng can be called using `fireproxng` or `fpng`.

<br>

## Usage

The help menu for the base utility is shown below:

```
Usage: fireproxng [OPTIONS] COMMAND [ARGS]...

  fireproxng is a tool for deploying AWS API Gateway proxies.

Options:
  -ak, --access_key TEXT          AWS Access Key ID
  -sk, --secret_access_key TEXT   AWS Secret Access Key
  -r, --region [us-east-1|us-east-2|us-west-1|us-west-2|ca-central-1|eu-west-1|eu-west-2|eu-central-1|ap-southeast-1|ap-southeast-2|ap-south-1|ap-northeast-1|ap-northeast-2|sa-east-1|cn-north-1]
                                  AWS Region
  -st, --session_token TEXT       AWS Session Token
  -p, --profile TEXT              AWS Profile
  -h, --help                      Show this message and exit.

Commands:
  create  Create a new fireproxng proxy.
  delete  Delete a fireproxng proxy.
  list    List all fireproxng proxies.
  update  Update a fireproxyng proxy.
```

All subcommands expect AWS credentials sourced from command line parameters, environment variables, or the aws credentials file (perfered). Major regions are supported.

The environment variables fireproxng can read from are as follows:

- access_key - AWS_ACCESS_KEY_ID
- secret_access_key - AWS_SECRET_ACCESS_KEY
- region - AWS_REGION

To specify a profile in your existing AWS credentials file, use the `-p` or `--profile` flag.

<br>

### Create

An example help menu for the create subcommand is shown below:

```
Usage: fireproxng create [OPTIONS] TARGET...
```

When creating a new proxy endpoint, you can specify an arbitrary number of URLs to stage the API gateway. The tool will automatically generate a unique name for the proxy endpoint. For example you can do the following:

```
fpng create https://example.com https://example.com/api/v1 https://example.com/api/v2
```

This will stage multiple endpoints with the same name and different api-id values. You can additionally specify a list of URLs from a file:

```
fpng create /tmp/urls.txt
```

The file should contain one URL per line.

Output files in JSON format are also supported for tracking created existing endpoints and integrating with existing tools:

```
fpng create -o /tmp/proxies.json /tmp/urls.txt
```

<br>

### Delete

The same goes as above for the delete subcommand with the fireproxng enhanced capability to delete multiple endpoints at once. The help menu for the delete subcommand is shown below:

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

Similarly to the create subcommand, you can specify a list of API IDs from a file:

```
fpng delete /tmp/api_ids.txt
```

<br>

### List

fireproxng can also list existing API endpoints not in a deleted state. The help menu for the list subcommand is shown below:

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

## Example Usage

Create multiple API endpoints from the command line using the create subcommand while sourcing from environment variables:

```
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
fpng create https://example.com https://example.com/api/v1 https://example.com/api/v2
```

Delete all API endpoints using the delete subcommand while sourcing credentials from a profile:

```
fpng delete -p default all
```

List all API endpoints using the list subcommand while sourcing credentials from the command line:

```
fpng -ak AKIAIOSFODNN7EXAMPLE -sk wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY list
```

## Coming Soon

Some planned features coming in the next release:

- Create proxy endpoints across multiple regions
- Update fireproxng endpoint name when updating target
- Alternate service usage for proxying traffic
- Session token handling (This is borken currently and I don't know anyone who uses it)
- YAML config file support

<br>

## Thanks

- The original [fireprox](https://github.com/ustayready/fireprox) of course from ustayready.
- Evasion features added by the authors of [CredMaster](https://github.com/knavesec/CredMaster/blob/master/fire.py).
