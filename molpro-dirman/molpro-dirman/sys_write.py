# Methods and helpers for interacting actively with the local filesystem

import os
from pathlib import Path

from .config import base_project_directory
from .sys_read import is_valid_project_path

class ProjectMountException(Exception):
  "General exception during project mount attempt"

class ProjectMountFailure(ProjectMountException):
  "Unrecoverable failure during project mount attempt"

class ProjectMountExists(ProjectMountException):
  "Mount Failed because destination already exists"

class ProjectAlreadyMounted(ProjectMountException):
  "Mount already exists in the requested configuration"


def symlink_project(project_path: Path, current_project: bool, overwrite: bool=False) -> None:
  "Safely symlinks a project directory to the specified slot"
  if not is_valid_project_path(project_path, project_level_only=True):  # Check target path
    if not is_valid_project_path(project_path):
      raise ProjectMountFailure("Invalid target project - does it exist?")
    raise ProjectMountFailure("Invalid target project - path must be at the root of a project directory")
  
  # Check if need to overwrite path
  # Check if already mounted as requested
  # Check if already mounted elsewhere

  raise NotImplementedError("WiP")

