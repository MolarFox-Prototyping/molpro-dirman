# Methods and helpers for interacting actively with the local filesystem

import os
from pathlib import Path

from .config import Config, symlink_name
from .sys_read import Project

class ProjectSymLinkException(Exception):
  "General exception during project symlink attempt"

class ProjectSymLinkFailure(ProjectSymLinkException):
  "Unrecoverable failure during project symlink attempt"

class ProjectSymLinkExists(ProjectSymLinkException):
  "SymLink Failed because symlink location already exists"

class ProjectAlreadySymLinked(ProjectSymLinkException):
  "SymLink already exists in the requested configuration"


def move_main_to_aux(overwrite_existing: bool=False) -> Path:
  "Moves the current main project (if any) to its aux symlink point, returns aux symlink path"
  main_symlink_path = Config.base_symlink_directory() / Config.main_project_symlink_name()
  aux_symlink_path = Config.base_symlink_directory() / symlink_name(
    Project.active(suppress_errors=False), is_main=False
  )
  
  # Check if the auxiliary path already exists
  if aux_symlink_path.exists():
    if os.readlink(aux_symlink_path) == os.readlink(main_symlink_path):
      os.remove(main_symlink_path)
      return aux_symlink_path
    elif overwrite_existing:
      os.remove(aux_symlink_path)
    else:
      raise ProjectSymLinkExists("Aux symlink already exists, and does not point to expected destination")

  os.rename(main_symlink_path, aux_symlink_path)
  return aux_symlink_path


def unlink_projects(main_only: bool=True) -> None:
  "Unlinks the main project and, optionally, all other aux symlinks"


def unlink_specific_project(project_path: Path) -> None:
  "Unlinks all references to the specified project in symlink directory"


def symlink_project(
  project_path: Path, 
  is_main: bool, 
  overwrite: bool=False, 
  keep_old_main: bool=False,
  ignore_existing_symlinks: bool=False
) -> None:
  "Safely symlinks a project directory to the specified slot"
  if not Project.is_valid_path(project_path, project_level_only=True):  # Check target path
    if not Project.is_valid_path(project_path):
      raise ProjectSymLinkFailure("Invalid target project - does it exist?")
    raise ProjectSymLinkFailure("Invalid target project - path must be at the root of a project directory")

  expected_symlinks: list[Path] = []

  # Check if need to overwrite path
  symlink_path = Config.base_symlink_directory / symlink_name(project_path.parts[-1], is_main=is_main)
  if (symlink_path).exists():

    # Check if already symlinked as requested
    if os.readlink(symlink_path) == project_path:
      raise ProjectAlreadySymLinked(f"Project {project_path.parts[-1]} already symlinked at {symlink_path}")

    # Don't modify existing symlink unless overwrite mode enabled
    if not overwrite:
      raise ProjectSymLinkExists("The requested symlink point already exists")
    
    # Move / delete the existing symlink
    if is_main and keep_old_main:
      move_main_to_aux()
    else:
      os.remove(symlink_path)

  # Check if already symlinked from elsewhere (by mpdman in its current config)
  if (Project.symlinks_to(project_path)):
    pass

  os.symlink(project_path, symlink_path, target_is_directory=True)
