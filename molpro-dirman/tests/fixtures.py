# Pytest general-purpose fixtures for unit tests

import os
import uuid
import pytest
import tempfile
import random

from pathlib import Path
from typing import Callable

RANDOM_SUBDIRS = [0, 3]
RANDOM_FILES_PER_DIR = [0, 5]
RANDOM_README_SIZE = [256, 1024]
RANDOM_FILE_SIZE = [0, 16384]

@pytest.fixture
def generate_data() -> Callable[[int, int], bytes]:
  return lambda min_size, max_size: random.randbytes(random.randint(min_size, max_size))


@pytest.fixture
def temp_dir() -> Path:
  with tempfile.TemporaryDirectory() as tmp_dir:
    yield Path(tmp_dir)


@pytest.fixture
def structured_dir(temp_dir) -> Path:
  os.mkdir(temp_dir / "home")
  os.mkdir(temp_dir / "home" / "Documents")
  os.mkdir(temp_dir / "home" / "OtherFolder")

  project_dir = temp_dir / "home" / "Projects"
  os.mkdir(project_dir)
  os.mkdir(project_dir / "T-1234567")
  os.mkdir(project_dir / "DT-1234567")
  os.mkdir(project_dir / "DO-4256663")
  os.mkdir(project_dir / "ABCDEF-4567890")

  yield temp_dir


@pytest.fixture
def populated_dir(structured_dir, generate_data) -> Path:
  for key in (structured_dir / "home" / "Projects").iterdir():
    if key.is_dir():

      # Make readme
      with open(key / "README.md", "w") as fd:
        fd.write(generate_data(*RANDOM_README_SIZE))

      # Make some files in root dir
      for __ in random.randint(*RANDOM_FILES_PER_DIR):
        with open(key / str(uuid.uuid4()), "w") as fd2:
          fd2.write(generate_data(*RANDOM_FILE_SIZE))
      
      # Make some subdirs
      for _ in random.randint(*RANDOM_SUBDIRS):
        subdir_path = key / str(uuid.uuid4())
        os.mkdir(subdir_path)
        
        # Make some files in each subdir
        for __ in random.randint(*RANDOM_FILES_PER_DIR):
          with open(subdir_path / str(uuid.uuid4()), "w") as fd2:
            fd2.write(generate_data(*RANDOM_FILE_SIZE))

  yield structured_dir