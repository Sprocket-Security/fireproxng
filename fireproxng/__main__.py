#!/usr/bin/env python3

import json
import logging
import os
import sys

import click
from click_extra import config_option
from rich.console import Console
from rich.logging import RichHandler

from .lib.fire import FireProx
from .utils.process import Process

# Setting up logging with rich
FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

# Initializing console for rich
console = Console()


regions = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "ca-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-central-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-south-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "sa-east-1",
    "cn-north-1",
]

# Setting context settings for click
# click.rich_click.SHOW_METAVARS_COLUMN = False
# click.rich_click.SHOW_ARGUMENTS = True
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help", "help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-ak",
    "--access_key",
    envvar="AWS_ACCESS_KEY_ID",
    type=str,
    default=None,
    help="AWS Access Key ID",
)
@click.option(
    "-sk",
    "--secret_access_key",
    envvar="AWS_SECRET_ACCESS_KEY",
    type=str,
    default=None,
    help="AWS Secret Access Key",
)
@click.option(
    "-r",
    "--region",
    type=click.Choice(regions),
    envvar="AWS_REGION",
    default="us-east-1",
    help="AWS Region",
)
@click.option(
    "-st", "--session_token", type=str, default=None, help="AWS Session Token"
)
@click.option("-p", "--profile", type=str, default="default", help="AWS Profile")
@click.pass_context
def main(ctx, access_key, secret_access_key, region, session_token, profile):
    """
    fireproxng is a tool for deploying AWS API Gateway proxies.
    """
    ctx.ensure_object(dict)
    ctx.obj["ACCESS_KEY"] = access_key
    ctx.obj["SECRET_ACCESS_KEY"] = secret_access_key
    ctx.obj["REGION"] = region
    ctx.obj["SESSION_TOKEN"] = session_token
    ctx.obj["PROFILE"] = profile
    pass


@main.command(no_args_is_help=False, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option(
    "-o",
    "--output",
    type=click.Path(writable=True, dir_okay=False),
    required=False,
    help="Optional output file",
)
@click.argument("target", nargs=-1, type=str, required=True)
def create(ctx, target, output):
    """
    Create a new fireproxng proxy. \n
    Supports multiple targets or file of targets. \n
    Supports output JSON file of API Gateway IDs. \n
    Example: fpng create /path/to/targets.txt
    """

    # Check if target is a file
    try:
        if os.path.exists(target[0]) and len(target) == 1:

            # Convert tuple to string
            target = target[0]

            target = [line.strip() for line in open(target)]

    except Exception as a:
        log.error(f"Could not open file: {a}")
        exit(1)
    endpoints = {}
    for target in target:

        parser = Process(
            ctx.obj["PROFILE"],
            ctx.obj["ACCESS_KEY"],
            ctx.obj["SECRET_ACCESS_KEY"],
            ctx.obj["SESSION_TOKEN"],
            ctx.obj["REGION"],
            target,
        )
        template = parser.build_template()
        client, region = parser.auth_config_handler()

        # Initializing FireProx
        fire = FireProx(client, template, region, target)

        # Creating API Gateway proxy
        endpoint = fire.create()

        # Append endpoint to endpoints dict
        endpoints[target] = endpoint

    # Outputing endpoints to JSON file
    if output:
        # Check if output file exists
        if os.path.exists(output):
            log.error(f"File {output} already exists.")
            if click.confirm("Do you want to overwrite it?"):
                with open(output, "w") as f:
                    json.dump(endpoints, f, indent=4)
        else:
            with open(output, "w") as f:
                json.dump(endpoints, f, indent=4)


@main.command(no_args_is_help=False, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def list(ctx):
    """List all fireproxng proxies. \n
    Example: fpng list \n
    """

    parser = Process(
        ctx.obj["PROFILE"],
        ctx.obj["ACCESS_KEY"],
        ctx.obj["SECRET_ACCESS_KEY"],
        ctx.obj["SESSION_TOKEN"],
        ctx.obj["REGION"],
        None,
    )
    client, region = parser.auth_config_handler()

    # Initializing FireProx
    fire = FireProx(client, None, region, None)

    # Listing API Gateway proxies
    fire.list()


@main.command(no_args_is_help=False, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument("api_ids", nargs=-1, required=False, type=str)
def delete(ctx, api_ids):
    """Delete a fireproxng proxy. \n
    Supports multiple API IDs or file of API IDs. \n
    You can also delete all proxies by passing all in as the API ID. \n
    Example: fpng delete /path/to/api_ids.txt
    """

    # Check if target is a file
    try:
        if os.path.exists(api_ids[0]) and len(api_ids) == 1:

            # Convert tuple to string
            api_ids = api_ids[0]

            api_ids = [line.strip() for line in open(api_ids)]

    except Exception as a:
        log.error(f"Could not open file: {a}")
        exit(1)

    for api_id in api_ids:
        parser = Process(
            ctx.obj["PROFILE"],
            ctx.obj["ACCESS_KEY"],
            ctx.obj["SECRET_ACCESS_KEY"],
            ctx.obj["SESSION_TOKEN"],
            ctx.obj["REGION"],
            None,
        )
        client, region = parser.auth_config_handler()

        # Initializing FireProx
        fire = FireProx(client, None, region, None, api_id)

        results = []
        result = fire.delete()[0]
        results.append(result["ResponseMetadata"]["HTTPStatusCode"])

    if api_id == "all":

        # If all results are 202, then all proxies were deleted
        if all(result == 202 for result in results):
            log.info("All proxies were deleted.")
        else:
            log.error("Could not delete all proxies. Check logs for more info.")

    else:
        log.info(f"fireproxng proxy - {api_id} has been deleted successfully.")


@main.command(no_args_is_help=False, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument("api_id", type=str)
@click.argument("target", type=str)
def update(ctx, api_id, target):
    """Update a fireproxyng proxy. \n
    Example: fpng update <api_id> <target>
    """

    parser = Process(
        ctx.obj["PROFILE"],
        ctx.obj["ACCESS_KEY"],
        ctx.obj["SECRET_ACCESS_KEY"],
        ctx.obj["SESSION_TOKEN"],
        ctx.obj["REGION"],
        None,
    )
    client, region = parser.auth_config_handler()

    # Initializing FireProx
    fire = FireProx(client, None, region, target, api_id)

    # Updating API Gateway proxy
    console.print(fire.update())


if __name__ == "__main__":
    main()
