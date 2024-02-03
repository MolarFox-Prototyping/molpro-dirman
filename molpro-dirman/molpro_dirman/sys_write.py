# Methods and helpers for interacting actively with the local filesystem

import os
import re
from pathlib import Path

from .config import Config, symlink_name
from .sys_read import Project
from .errors import (
  ProjectSymLinkExists, 
  ProjectSymLinkFailure, 
  ProjectSymlinkedElsewhere, 
  ProjectAlreadySymLinked
)

def delete_symlink(path: Path, mpdman_only=True) -> Path:
  "Safe method to delete only symlinks. Also can perform check to ensure it is an mpdman-created symlink"
  if not os.path.islink(path):
    raise ValueError("Delete symlink called on a file object that is not a symlink")
  if mpdman_only and not Config.matches_symlink_regex(path):
    raise ValueError("Symlink does not match project symlink regex")

  os.remove(path)
  return path


def move_main_to_aux(overwrite_existing: bool=False) -> Path:
  "Moves the current main project (if any) to its aux symlink point, returns aux symlink path"
  main_symlink_path = Config.base_symlink_directory() / Config.main_project_symlink_name()
  aux_symlink_path = Config.base_symlink_directory() / symlink_name(
    Project.active(suppress_errors=False), is_main=False
  )
  
  # Check if the auxiliary path already exists
  if aux_symlink_path.exists():
    if os.readlink(aux_symlink_path) == os.readlink(main_symlink_path):
      delete_symlink(main_symlink_path)
      return aux_symlink_path
    elif overwrite_existing:
      delete_symlink(aux_symlink_path)
    else:
      raise ProjectSymLinkExists("Aux symlink already exists, and does not point to expected destination")

  os.rename(main_symlink_path, aux_symlink_path)
  return aux_symlink_path


def unlink_all(main_only: bool=False) -> list[Path]:
  "Unlinks the main project and, optionally, all other aux symlinks - returns list of removed symlinks"
  if main_only:
    return [delete_symlink(Config.base_symlink_directory() / Config.main_project_symlink_name())]
  
  return [
    delete_symlink(s, mpdman_only=True) for s in Project.all_symlinks(mpdman_only=True)
  ]


def unlink_specific(project_path: Path) -> list[Path]:
  "Unlinks all references to the specified project in symlink directory - returns list of removed symlinks"
  return [delete_symlink(s) for s in Project.symlinks_to(project_path)]


def symlink_project(
  project_path: Path, 
  is_main: bool, 
  overwrite: bool=False, 
  keep_old_main: bool=False,
  ignore_existing_symlinks: bool=False
) -> Path:
  "Safely symlinks a project directory to the specified slot"
  if not Project.is_valid_path(project_path, project_level_only=True):  # Check target path
    if not Project.is_valid_path(project_path):
      raise ProjectSymLinkFailure("Invalid target project - does it exist?")
    raise ProjectSymLinkFailure("Invalid target project - path must be at the root of a project directory")

  # Check if need to overwrite path
  symlink_path = Config.base_symlink_directory() / symlink_name(project_path.parts[-1], is_main=is_main)
  if (symlink_path).exists():

    # Check if already symlinked as requested
    if Path(os.readlink(symlink_path)) == project_path:
      raise ProjectAlreadySymLinked(f"Project {project_path.parts[-1]} already symlinked at {symlink_path}")

    # Don't modify existing symlink unless overwrite mode enabled
    if not overwrite:
      raise ProjectSymLinkExists("The requested symlink point already exists")
    
    # Move / delete the existing symlink
    if is_main and keep_old_main:
      move_main_to_aux()
    else:
      delete_symlink(symlink_path)

  # Check if already symlinked from elsewhere (by mpdman in its current config)
  if not ignore_existing_symlinks and (existing_symlinks := Project.symlinks_to(project_path)):
    raise ProjectSymlinkedElsewhere(f"Project {project_path.parts[-1]} is already linked elsewhere: {existing_symlinks}")

  os.symlink(project_path, symlink_path, target_is_directory=True)
  return symlink_path
