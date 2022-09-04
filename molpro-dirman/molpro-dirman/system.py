# Methods and helpers for interacting with the local filesystem

from pathlib import Path
from datetime import datetime

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
def base_project_directory() -> Path:
  "Directory path object within which all project directories are being stored"
  return Path.home() / "Projects"   # TODO: generalise this later


def project_dir_paths() -> list[Path]:
  "List of path objects for every project directory"
  return ls_d(base_project_directory())


def project_dirs() -> list[str]:
  "List of project directory names only"
  return extract_filenames(project_dir_paths())
