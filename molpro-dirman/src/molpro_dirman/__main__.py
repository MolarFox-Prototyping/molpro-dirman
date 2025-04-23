#!/bin/python3

# molpro_dirman: CLI tool to manage project serials locally
# Copyright (C) 2022 MolarFox Prototyping

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

import os
import typer
from InquirerPy import inquirer

from pathlib import Path
from textwrap import dedent
from rich.table import Table
from typing import Optional

from . import print, print_json
from .config import Config, Prefixes
from .local_read import Project, last_modified
from .local_write import delete_symlink, symlink_project, unlink_main, create_project
from .errors import ProjectSymLinkException

app = typer.Typer(invoke_without_command=True)


@app.command()
def status():
    "Output mounted project(s), and most recently activated projects"
    active()
    print()
    ls()


@app.command()
def active():
    "Output currently active project(s) only"
    links = Project.all_symlinks()
    records = sorted([
        [last_modified(l), l.parts[-1], Path(os.readlink(l)).parts[-1]]
        for l in links
    ])

    table = Table(title="Mounted projects (date_desc)")
    table.add_column("symlink", style="dodger_blue1")
    table.add_column("project", style="magenta")
    table.add_column("last_modified", style="bright_black")

    [table.add_row(p[1], p[2], p[0]) for p in records]
    print(table)


@app.command()
def ls():
    "List active projects, and local projects that are ready to be made active"
    records = sorted([[last_modified(p), p.parts[-1]] for p in Project.list_paths()], reverse=True)

    table = Table(title="Available Projects (date_desc)")
    table.add_column("project", style="magenta")
    table.add_column("last_modified", style="bright_black")

    [table.add_row(p[1], p[0]) for p in records]
    print(table)


@app.command()
def activate(project_name: str):
  "Activate a project"
  try:
    symlink_project(Config.base_project_directory() / project_name, is_main=True)
    print(f"[bold green]Linked '{project_name}' at \"{Config.base_project_directory() / project_name}\"[/bold green]")
  except ProjectSymLinkException as e:
    print(f"[bold red]{e}[/bold red]")



@app.command()
def deactivate(project_name: str=typer.Argument("main")):
  "Deactivate an active project"

  if not Project.active():
    return print(f"No main project set! No changes made.")

  full_path = Config.base_project_directory() / project_name
  removed: list[Path] = []
  match project_name:
    case "main":
      removed = unlink_main()
    case "all":
      removed = unlink_all()
    case _:
      removed = unlink_specific(full_path)

  print("[bold green]Removed paths:[/bold green]")
  for path in removed:
    print("  -", path)


@app.command()
def create(
    prefixes: list[str]=[],
    title: str=typer.Option(None, prompt="Project title"),
    description: str="",
    serial: Optional[int]=None
  ):
    "Create a new project"

    # Prompt for prefixes
    if not prefixes:
      prefixes = inquirer.checkbox(
        message="Select prefixes relevant to the new project:",
        choices=[{"value":k, "name": f"{k} - {v.short}"} for k, v in Prefixes.definitions().items()],
      ).execute()

    # Optionally prompt with editor for description to be edited
    if not description:
      if typer.confirm("Edit project description?", default=True):
        description = typer.edit() or ""

    # Validate prefixes were defined
    if not prefixes:
      print("[bold red]No prefixes were specified! Aborting[/bold red]")
      return
    
    # Create project
    project_path = create_project(prefixes, title, description, serial)
    project_name = project_path.parts[-1]

    print(f"[green]Created new project [bold][{project_name}][/bold][/green]")

    # Make that the new main
    unlink_main()
    activate(project_name)


@app.command()
def about():
  "Output some information about molpro_dirman"
  print(dedent(
    f"""
    MolarFox Prototyping: Project Directory Manager
    [italic]Version {Config.version()} - 2025[/italic]
    """
    ))


@app.command()
def prefixes(
        verbose: bool = typer.Option(False, help="Display long descriptions for serials")
):
    "List info about serial prefixes"
    if verbose:
        print_json(data=Prefixes.as_dict())
    else:
        print_json(data={s: info.short for s, info in Prefixes.definitions().items()})


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:  # Print status if no subcommand
        status()


if __name__ == "__main__":
    app()
