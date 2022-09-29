# Methods and helpers for interacting passively with the local filesystem

from distutils.command.config import config
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
  def all_symlinks(mpdman_only: bool=True) -> list[Path]:
    "Find all symlinks that exist in symlink dir, optionally including even ones not made in mpdman"
    return [
      key for key in 
      Config.base_symlink_directory().iterdir() if (
        os.path.islink(key) and
        (
          re.fullmatch(Config.symlink_name_regex(), key.parts[-1]) is not None or
          not mpdman_only
        )
      )
    ]


  @staticmethod
  def symlinks_to(path: Path, mpdman_only: bool=True) -> list[Path]:
    "Find all symlinks to the target project path in symlink directory / only ones made by this program"
    if not Project.is_valid_path(path, project_level_only=True):
      raise ValueError("Path did not point to valid, top-level project directory")

    return [
      key for key in 
      Project.all_symlinks(mpdman_only=mpdman_only)
      if Path(os.readlink(key)) == path
    ]


  @staticmethod
  def is_valid_path(path: Path, project_level_only: bool=False) -> bool:
    "Verify a path is validly within a project (or is project directory, if param set)"
    try:
      return (
        path.exists() and
        (
          (
            len(path.relative_to(Config.base_project_directory()).parts) == 1 and
            path.relative_to(Config.base_project_directory()).parts[-1] == path.parts[-1]
          ) or not project_level_only
        )
      )
    except ValueError:
      return False
