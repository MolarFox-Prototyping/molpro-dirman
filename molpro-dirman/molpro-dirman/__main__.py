#!/bin/python3

# molpro-dirman: CLI tool to manage project serials locally
# Copyright (C) 2022 MolarFox

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import typer

app = typer.Typer(invoke_without_command=True)


@app.command()
def status():
    "Output mounted project(s), most recent n projects"


@app.command()
def active():
    "Output currently active project(s)"


@app.command()
def ls():
    "List projects that currently exist locally, and can be made active"


@app.command()
def activate():
    "Activate a project"


@app.command()
def deactivate():
    "Deactivate an active project"


@app.command()
def create():
    "Create a new project"


@app.command()
def about():
    "Output some information about molpro-dirman"


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:  # Print status if no subcommand
        status()


if __name__ == "__main__":
    app()