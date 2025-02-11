# Test passive system interaction methods

from unittest.mock import MagicMock
from datetime import datetime
from shutil import rmtree

from . import local_read, config
from tests.fixtures import *

def test_ls_dirs_only(populated_dir):
  for pj_key in (populated_dir / "home" / "Projects").iterdir():
    if pj_key.is_dir():
      output = local_read.ls_d(pj_key)
      assert all(key.is_dir() for key in output)
      assert len(output) <= len(list(pj_key.iterdir()))


def test_extract_filenames(populated_dir):
  output = local_read.extract_filenames(
    list((populated_dir / "home" / "Projects").iterdir())
  )

  assert output
  assert all(name and isinstance(name, str) for name in output)
  assert all('/' not in name for name in output)


def test_last_modified(datetimed_dir):
  def run_and_sort(*args, **kwargs) -> list[str]:
    return local_read.extract_filenames([
      x[1] for x in sorted([
        [local_read.last_modified(key, *args, **kwargs), key] for key in
        local_read.ls_d(datetimed_dir / "home" / "Projects")
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

  output = local_read.Project.list_paths()
  assert all(isinstance(k, Path) for k in output)
  for pj_key in (populated_dir / "home" / "Projects").iterdir():
    if pj_key.is_dir():
      assert pj_key in output


def test_project_list_names(populated_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=populated_dir / "home" / "Projects"
  )

  output = local_read.Project.list_names()
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

  assert local_read.Project.active() == "DO-4256663"


def test_project_active_non_existent(structured_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=structured_dir / "home" / "Projects"
  )
  config.Config.base_symlink_directory = MagicMock(
    return_value=structured_dir / "home"
  )

  assert local_read.Project.active() is None
  with pytest.raises(FileNotFoundError):
    local_read.Project.active(suppress_errors=False)


def test_project_all_symlinks(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )

  tests = [
    {
      "kwargs": {"mpdman_only": False},
      "expected": ["current_project", "project_T-1234567", "project_DT-1234567", "my_custom_symlink_awooo", "ohman_love_documents"]
    },
    {
      "kwargs": {"mpdman_only": True},
      "expected": ["current_project", "project_T-1234567", "project_DT-1234567"]
    },
  ]

  for test in tests:
    output = local_read.Project.all_symlinks(**test["kwargs"])
    assert set(key.parts[-1] for key in output) == set(test["expected"])

  rmtree(populated_dir / "home")
  os.mkdir(populated_dir / "home")
  assert local_read.Project.all_symlinks() == []


def test_project_symlinks_to(populated_dir):
  project_base_dir = populated_dir / "home" / "Projects"
  symlink_base_dir = populated_dir / "home"

  config.Config.base_project_directory = MagicMock(
    return_value=project_base_dir
  )
  config.Config.base_symlink_directory = MagicMock(
    return_value=symlink_base_dir
  )
  
  tests = [
    {
      "kwargs": {"path": project_base_dir / "DO-4256663", "mpdman_only": False},
      "expected": [symlink_base_dir / "current_project"]
    },
    {
      "kwargs": {"path": project_base_dir / "DT-1234567", "mpdman_only": False},
      "expected": [symlink_base_dir / "project_DT-1234567"]
    },
    {
      "kwargs": {"path": project_base_dir / "ABCDEF-4567890", "mpdman_only": False},
      "expected": [symlink_base_dir / "my_custom_symlink_awooo"]
    },
    {
      "kwargs": {"path": project_base_dir / "ABCDEF-4567890", "mpdman_only": True},
      "expected": []
    },
  ]

  for test in tests:
    output = local_read.Project.symlinks_to(**test["kwargs"])
    assert set(output) == set(test["expected"])

  with pytest.raises(ValueError):
    local_read.Project.symlinks_to(symlink_base_dir / "Documents")


def test_project_is_valid_path(populated_dir):
  config.Config.base_project_directory = MagicMock(
    return_value=populated_dir / "home" / "Projects"
  )

  for pj_key in (populated_dir / "home" / "Projects").iterdir():
    if pj_key.is_dir():
      assert local_read.Project.is_valid_path(pj_key) is True
      assert local_read.Project.is_valid_path(pj_key, project_level_only=True) is True

      randfile = random.choice([
        key for key in pj_key.iterdir()
      ])

      assert local_read.Project.is_valid_path(randfile) is True
      assert local_read.Project.is_valid_path(randfile, project_level_only=True) is False

  assert local_read.Project.is_valid_path(populated_dir / "home" / "Documents") is False
  assert local_read.Project.is_valid_path(populated_dir / "fake_path" / "Projects") is False
