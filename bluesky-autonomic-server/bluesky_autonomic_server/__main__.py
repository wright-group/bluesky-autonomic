#!/usr/bin/env python3


import os
import pathlib
import subprocess
import sys

import click

from .__version__ import __version__
from ._server import Server


@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        launch()


@main.command()
@click.option('--rpc-port', default=13560, help='TCP port to serve JSON-RPC interface on.')
@click.option('--pub-port', default=13561, help='TCP port to publish zmq messages on.')
@click.option('--debug', default=False, is_flag=True)
def launch(rpc_port, pub_port, debug):
    Server(rpc_port, pub_port, debug)
