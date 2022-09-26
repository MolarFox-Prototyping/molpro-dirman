# Methods and helpers for interacting actively with the local filesystem

import os
from pathlib import Path

from .config import base_project_directory, base_symlink_directory, main_project_symlink_name, symlink_name
from .sys_read import Project

class ProjectSymLinkException(Exception):
  "General exception during project symlink attempt"

class ProjectSymLinkFailure(ProjectSymLinkException):
  "Unrecoverable failure during project symlink attempt"

class ProjectSymLinkExists(ProjectSymLinkException):
  "SymLink Failed because symlink location already exists"

class ProjectAlreadySymLinked(ProjectSymLinkException):
  "SymLink already exists in the requested configuration"


def main_project_to_aux(ignore_no_main: bool=False) -> None:
  "Moves the current main project (if any) to its aux symlink point"
  os.rename(
    base_symlink_directory() / main_project_symlink_name(), 
    base_symlink_directory() / symlink_name(
      Project.active(suppress_errors=ignore_no_main), is_main=False
    )
  )


def symlink_project(project_path: Path, is_main: bool, overwrite: bool=False, keep_old_main=False) -> None:
  "Safely symlinks a project directory to the specified slot"
  if not Project.is_valid_path(project_path, project_level_only=True):  # Check target path
    if not Project.is_valid_path(project_path):
      raise ProjectSymLinkFailure("Invalid target project - does it exist?")
    raise ProjectSymLinkFailure("Invalid target project - path must be at the root of a project directory")
  
  # Check if need to overwrite path
  symlink_path = base_symlink_directory() / symlink_name(project_path.parts[-1], is_main=is_main)
  if (symlink_path).exists():

    # Check if already symlinked as requested
    if os.readlink(symlink_path) == project_path:
      raise ProjectAlreadySymLinked(f"Project {project_path.parts[-1]} already symlinked at {symlink_path}")

    # Don't modify existing symlink unless overwrite mode enabled
    if not overwrite:
      raise ProjectSymLinkExists("The requested symlink point already exists")
    
    # Move / delete the existing symlink
    if is_main and keep_old_main:
      main_project_to_aux()
    else:
      os.remove(symlink_path)

  # Check if already symlinked from elsewhere

  os.symlink(project_path, symlink_path, target_is_directory=True)
