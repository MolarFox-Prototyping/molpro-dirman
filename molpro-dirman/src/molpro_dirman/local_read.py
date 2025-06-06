# Methods and helpers for interacting passively with the local filesystem

import os
from pathlib import Path
from datetime import datetime
import re
from typing import Optional

from .config import Config

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# GENERAL UTILS
def ls_d(path: Path) -> list[Path]:
  "List of all subdirectories of specified directory"
  return [key for key in path.iterdir() if key.is_dir()]


def extract_filenames(objects: list[Path]) -> list[str]:
  "List of file / directory names only, from list of paths"
  return [obj.parts[-1] for obj in objects]


def last_modified(path: Path, recursively_check=True) -> str:
  "Last modified time of a directory, optionally based on all recursive children"
  if not recursively_check:  # Just check directory's access / mod time
    return datetime.fromtimestamp(
      max(path.stat().st_atime, path.stat().st_mtime)
    ).strftime(DATETIME_FORMAT)

  # Check directory, subdirectories, and all children for the most recent atime / mtime
  return datetime.fromtimestamp(
    max(
      max(obj.stat().st_atime, obj.stat().st_mtime) for obj in path.rglob('*')
    )
  ).strftime(DATETIME_FORMAT)


class Project:

  @staticmethod
  def list_paths() -> list[Path]:
    "List of path objects for every project directory"
    return ls_d(Config.base_project_directory())

  @staticmethod
  def list_names() -> list[str]:
    "List of project directory names only"
    return extract_filenames(Project.list_paths())

  @staticmethod
  def active(suppress_errors=True) -> Optional[str]:
    "Name of currently active project, if any"
    try:
      return Path(
        os.readlink(
          Config.base_symlink_directory() / Config.main_project_symlink_name()
        )
      ).parts[-1]
    except FileNotFoundError as e:
      if suppress_errors:
        return None
      raise e

  @staticmethod
  def all_symlinks(mpdman_only: bool = True) -> list[Path]:
    "Find all symlinks that exist in symlink dir, optionally including even ones not made in mpdman"
    return [
      key for key in
      Config.base_symlink_directory().iterdir() if (
        os.path.islink(key) and
        (
          not mpdman_only or
          Config.matches_symlink_regex(key)
        )
      )
    ]

  @staticmethod
  def symlinks_to(path: Path, mpdman_only: bool = True) -> list[Path]:
    "Find all symlinks to the target project path in symlink directory / only ones made by this program"
    if not Project.is_valid_path(path):
      raise ValueError("Path did not point to valid project directory")

    return [
      key for key in
      Project.all_symlinks(mpdman_only=mpdman_only)
      if Path(os.readlink(key)) == path
    ]

  @staticmethod
  def is_valid_path(path: Path) -> bool:
    "Verify a path is validly within a project (or is project directory, if param set)"
    try:
      return bool(
        path.exists() and path.relative_to(Config.base_project_directory())
      )
    except ValueError:
      return False  # ValueError is raised if the path is not under the project directory
