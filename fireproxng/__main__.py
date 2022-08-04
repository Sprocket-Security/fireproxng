#!/usr/bin/env python3

import logging
import sys

import rich_click as click
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
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.SHOW_ARGUMENTS = True

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
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help", "help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    fireprox-ng is a tool for deploying AWS API Gateway proxies.
    """
    pass


@main.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
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
@click.argument("profile_name", default="default")
@click.argument("target", nargs=-1)
def create(profile_name, access_key, secret_access_key, session_token, region, target):
    """
    Create a new fireprox-ng proxy.
    """
    for target in target:

        parser = Process(
            profile_name, access_key, secret_access_key, session_token, region, target
        )
        template = parser.build_template()
        client, region = parser.auth_config_handler()

        # Initializing FireProx
        fire = FireProx(client, template, region, target)

        # Creating API Gateway proxy
        fire.create()


@main.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
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
@click.option("-st", "--session_token", type=str, default=None)
@click.argument("profile_name", default="default")
def list(profile_name, access_key, secret_access_key, session_token, region):
    """List all fireprox-ng proxies."""
    parser = Process(
        profile_name, access_key, secret_access_key, session_token, region, None
    )
    client, region = parser.auth_config_handler()

    # Initializing FireProx
    fire = FireProx(client, None, region, None)

    # Listing API Gateway proxies
    fire.list()


@main.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
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
@click.option("-st", "--session_token", type=str, default=None)
@click.argument("profile_name", default="default")
@click.argument("api_id", nargs=-1)
def delete(profile_name, access_key, secret_access_key, session_token, region, api_id):
    """Delete a fireprox-ng proxy."""
    for api_id in api_id:
        parser = Process(
            profile_name, access_key, secret_access_key, session_token, region, None
        )
        client, region = parser.auth_config_handler()

        # Initializing FireProx
        fire = FireProx(client, None, region, None, api_id)

        result = fire.delete()

        # Deleting API Gateway proxy
        if api_id == "all":
            log.info("All fireprox-ng proxies have been deleted successfully.")
        else:
            log.info(f"fireprox-ng proxy {api_id} has been deleted successfully.")


@main.command(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
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
@click.option("-st", "--session_token", type=str, default=None)
@click.argument("profile_name", default="default")
@click.argument("api_id", type=str)
@click.argument("target", type=str)
def update(
    profile_name, access_key, secret_access_key, session_token, region, api_id, target
):
    """Update a fireproxy-ng proxy."""
    parser = Process(
        profile_name, access_key, secret_access_key, session_token, region, None
    )
    client, region = parser.auth_config_handler()

    # Initializing FireProx
    fire = FireProx(client, None, region, target, api_id)

    # Updating API Gateway proxy
    console.print(fire.update())


if __name__ == "__main__":
    main()
