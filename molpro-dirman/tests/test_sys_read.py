# Test passive system interaction methods

from unittest.mock import MagicMock
from datetime import datetime

from . import sys_read, config
from tests.fixtures import *

def test_ls_dirs_only(populated_dir):
  for pj_key in (populated_dir / "home" / "Projects").iterdir():
    if pj_key.is_dir():
      output = sys_read.ls_d(pj_key)
      assert all(key.is_dir() for key in output)
      assert len(output) <= len(list(pj_key.iterdir()))


def test_extract_filenames(populated_dir):
  output = sys_read.extract_filenames(
    list((populated_dir / "home" / "Projects").iterdir())
  )

  assert output
  assert all(name and isinstance(name, str) for name in output)
  assert all('/' not in name for name in output)


def test_last_modified(datetimed_dir):
  def run_and_sort(*args, **kwargs) -> list[str]:
    return sys_read.extract_filenames([
      x[1] for x in sorted([
        [sys_read.last_modified(key, *args, **kwargs), key] for key in
        sys_read.ls_d(datetimed_dir / "home" / "Projects")
      ])
    ])

  output1 = run_and_sort(recursively_check=True)
  assert output1.index("DO-4256663") > output1.index("T-1234567")

  output2 = run_and_sort(recursively_check=False)
  assert output2.index("DO-4256663") < output2.index("T-1234567")


def test_project_list_paths(populated_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=populated_dir / "home" / "Projects"
  )

  output = sys_read.Project.list_paths()
  assert all(isinstance(k, Path) for k in output)
  for pj_key in (populated_dir / "home" / "Projects").iterdir():
    if pj_key.is_dir():
      assert pj_key in output


def test_project_list_names(populated_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=populated_dir / "home" / "Projects"
  )

  output = sys_read.Project.list_names()
  assert all(isinstance(x, str) for x in output)
  for pj_key in (populated_dir / "home" / "Projects").iterdir():
    if pj_key.is_dir():
      assert pj_key.parts[-1] in output


def test_project_active_existent(populated_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=populated_dir / "home" / "Projects"
  )
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )

  assert sys_read.Project.active() == "DO-4256663"


def test_project_active_non_existent(structured_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=structured_dir / "home" / "Projects"
  )
  config.Config.base_symlink_directory = MagicMock(
    return_value=structured_dir / "home"
  )

  assert sys_read.Project.active() is None
  with pytest.raises(FileNotFoundError):
    sys_read.Project.active(suppress_errors=False)


def test_project_is_valid_path(populated_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=populated_dir / "home" / "Projects"
  )

  for pj_key in (populated_dir / "home" / "Projects").iterdir():
    if pj_key.is_dir():
      assert sys_read.Project.is_valid_path(pj_key) is True
      assert sys_read.Project.is_valid_path(pj_key, project_level_only=True) is True

      randfile = random.choice([
        pj_key for pj_key in (populated_dir / "home" / "Projects").iterdir()
      ])

      assert sys_read.Project.is_valid_path(pj_key) is True
      assert sys_read.Project.is_valid_path(pj_key, project_level_only=True) is False

  assert sys_read.Project.is_valid_path(populated_dir / "fake_path" / "Projects") is False
