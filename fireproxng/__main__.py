#!/usr/bin/env python3

import logging
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
@click.config_option(section="fireproxng")
def main(ctx, access_key, secret_access_key, region, session_token, profile):
    """
    fireprox-ng is a tool for deploying AWS API Gateway proxies.
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
@click.argument("target", nargs=-1)
@config_option(strict=True)
def create(ctx, target):
    """
    Create a new fireprox-ng proxy.
    """
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
        fire.create()


@main.command(no_args_is_help=False, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def list(ctx):
    """List all fireprox-ng proxies."""

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
# def delete(access_key, secret_access_key, region, session_token, profile_name, api_ids):
def delete(ctx, api_ids):
    """Delete a fireprox-ng proxy."""

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

        result = fire.delete()
        console.print(result)

        # Deleting API Gateway proxy
        if api_id == "all":
            log.info("All fireprox-ng proxies have been deleted successfully.")
        else:
            log.info(f"fireprox-ng proxy {api_id} has been deleted successfully.")


@main.command(no_args_is_help=False, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument("api_id", type=str)
@click.argument("target", type=str)
def update(ctx, api_id, target):
    """Update a fireproxy-ng proxy."""
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
