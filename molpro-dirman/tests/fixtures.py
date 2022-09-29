# Pytest general-purpose fixtures for unit tests

import os
import uuid
import pytest
import random
from datetime import datetime, timedelta

from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock

from . import config

RANDOM_SUBDIRS = [0, 3]
RANDOM_FILES_PER_DIR = [0, 5]
RANDOM_README_SIZE = [256, 1024]
RANDOM_FILE_SIZE = [0, 16384]

@pytest.fixture
def generate_data() -> Callable[[int, int], bytes]:
  return lambda min_size, max_size: random.randbytes(random.randint(min_size, max_size))


@pytest.fixture
def mock_base_directories() -> Callable[[Path], None]:
  def _mock_base_directories(base_path: Path) -> None:
    config.Config.base_project_directory = MagicMock(
      return_value=base_path / "home" / "Projects"
    )
    config.Config.base_symlink_directory = MagicMock(
      return_value=base_path / "home"
    )

  return lambda p: _mock_base_directories(p)


@pytest.fixture
def structured_dir(tmpdir) -> Path:
  os.mkdir(tmpdir / "home")
  os.mkdir(tmpdir / "home" / "Documents")
  os.mkdir(tmpdir / "home" / "OtherFolder")

  project_dir = tmpdir / "home" / "Projects"
  os.mkdir(project_dir)
  os.mkdir(project_dir / "T-1234567")
  os.mkdir(project_dir / "DT-1234567")
  os.mkdir(project_dir / "DO-4256663")
  os.mkdir(project_dir / "ABCDEF-4567890")
  os.mkdir(project_dir / "APJ-1234567")

  os.utime(project_dir / "T-1234567", (
    (datetime.now() + timedelta(days=90)).timestamp(),  # atime
    (datetime.now() + timedelta(days=81)).timestamp()   # mtime
  ))

  os.utime(project_dir / "DO-4256663", (
    (datetime.now() + timedelta(days=76)).timestamp(),  # atime
    (datetime.now() + timedelta(days=21)).timestamp()   # mtime
  ))

  yield Path(tmpdir)


@pytest.fixture
def populated_dir(structured_dir, generate_data) -> Path:
  for key in (structured_dir / "home" / "Projects").iterdir():
    if key.is_dir():

      # Make readme
      with open(key / "README.md", "wb") as fd:
        fd.write(generate_data(*RANDOM_README_SIZE))

      # Make some files in root dir
      for __ in range(random.randint(*RANDOM_FILES_PER_DIR)):
        with open(key / str(uuid.uuid4()), "wb") as fd2:
          fd2.write(generate_data(*RANDOM_FILE_SIZE))
      
      # Make some subdirs
      for _ in range(random.randint(*RANDOM_SUBDIRS)):
        subdir_path = key / str(uuid.uuid4())
        os.mkdir(subdir_path)
        
        # Make some files in each subdir
        for __ in range(random.randint(*RANDOM_FILES_PER_DIR)):
          with open(subdir_path / str(uuid.uuid4()), "wb") as fd2:
            fd2.write(generate_data(*RANDOM_FILE_SIZE))

  os.symlink(
    structured_dir / "home" / "Projects" / "DO-4256663", 
    structured_dir / "home" / "current_project", 
    target_is_directory=True
  )

  os.symlink(
    structured_dir / "home" / "Projects" / "T-1234567", 
    structured_dir / "home" / "project_T-1234567", 
    target_is_directory=True
  )

  os.symlink(
    structured_dir / "home" / "Projects" / "DT-1234567", 
    structured_dir / "home" / "project_DT-1234567", 
    target_is_directory=True
  )

  os.symlink(
    structured_dir / "home" / "Projects" / "ABCDEF-4567890",
    structured_dir / "home" / "my_custom_symlink_awooo", 
    target_is_directory=True
  )

  os.symlink(
    structured_dir / "home" / "Documents", 
    structured_dir / "home" / "ohman_love_documents", 
    target_is_directory=True
  )

  yield structured_dir


@pytest.fixture
def datetimed_dir(structured_dir, generate_data) -> Path:
  for key in (structured_dir / "home" / "Projects").iterdir():
    if key.is_dir():

      # Make readme
      with open(key / "README.md", "wb") as fd:
        fd.write(generate_data(*RANDOM_README_SIZE))
      os.utime(key / "README.md", (
        (datetime.now() - timedelta(days=256)).timestamp(),  # atime
        (datetime.now() - timedelta(days=301)).timestamp()   # mtime
      ))

  os.utime(structured_dir / "home" / "Projects"/ "DO-4256663" / "README.md", (
    (datetime.now() - timedelta(days=3)).timestamp(),  # atime
    (datetime.now() - timedelta(days=5)).timestamp()   # mtime
  ))

  yield structured_dir