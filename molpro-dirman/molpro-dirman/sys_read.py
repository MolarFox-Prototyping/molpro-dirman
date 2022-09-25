# Methods and helpers for interacting passively with the local filesystem

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import base_project_directory, base_symlink_directory, main_project_symlink_name, symlink_name

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# GENERAL UTILS
def ls_d(path: Path) -> list[Path]:
  "List of all subdirectories of specified directory"
  return [key for key in path.iterdir() if key.is_dir()]

def extract_filenames(objects: list[Path]) -> list[str]:
  "List of file / directory names only, from list of paths"
  return [obj.parts[-1] for obj in objects]


def last_modified(path: Path, recursively_check=True) -> datetime:
  "Last modified time of a directory, optionally based on all recursive children"
  if not recursively_check: # Just check directory's access / mod time
    return datetime.utcfromtimestamp(
      max(path.stat().st_atime, path.stat().st_mtime)
    ).strftime(DATETIME_FORMAT)

  # Check directory, subdirectories, and all children for the most recent atime / mtime
  return datetime.utcfromtimestamp(
    max(
      max(obj.stat().st_atime, obj.stat().st_mtime) for obj in path.rglob('*')
    )
  ).strftime(DATETIME_FORMAT)


# PROJECT DIRECTORY UTILS
def project_dir_paths() -> list[Path]:
  "List of path objects for every project directory"
  return ls_d(base_project_directory())


def project_dirs() -> list[str]:
  "List of project directory names only"
  return extract_filenames(project_dir_paths())


def active_project(suppress_errors=True) -> Optional[str]:
  "Name of currently active project, if any"
  try:
    return Path(
      os.readlink(
        base_symlink_directory() / main_project_symlink_name()
      )
    ).parts[-1]
  except FileNotFoundError as e:
    if suppress_errors: 
      return None
    raise e


def is_valid_project_path(path: Path, project_level_only: bool=False) -> bool:
  "Verify a path is validly within a project (or is project directory, if param set)"
  try:
    return (
      path.exists() and
      (
        len(path.relative_to(base_project_directory()).parts) == 1 or 
        not project_level_only
      )
    )
  except ValueError:
    return False
