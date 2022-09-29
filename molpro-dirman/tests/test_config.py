# Test config methods

import re
import json

from pathlib import Path
from . import config


def test_config_version():
  version: str = config.Config.version()
  assert len(version.split('.')) == 3


def test_config_base_project_directory():
  base_dir = config.Config.base_project_directory()

  assert config.Config.base_project_directory() == base_dir
  assert isinstance(base_dir, Path)
  assert base_dir.parts[-1] == "Projects"


def test_config_base_symlink_directory():
  symlink_dir = config.Config.base_symlink_directory()

  assert config.Config.base_symlink_directory() == symlink_dir
  assert isinstance(symlink_dir, Path)


def test_config_main_project_symlink_name():
  assert config.Config.main_project_symlink_name() == config.symlink_name("", is_main=True)


def test_config_symlink_name_regex():
  test_input = [
    "project_DT-1234567",
    "not_a_match",
    "project_peepee",
    "current_project",
    "project_AFS-3216548",
    "project_LONG-32165489",
    "project_ABCDEFG-3216548",
  ]
  tests = [
    {
      "kwargs": {"include_main": True, "include_aux": True},
      "expected": ["current_project", "project_DT-1234567", "project_AFS-3216548", "project_ABCDEFG-3216548"]
    },
    {
      "kwargs": {"include_main": True, "include_aux": False},
      "expected": ["current_project"]
    },
    {
      "kwargs": {"include_main": False, "include_aux": True},
      "expected": ["project_DT-1234567", "project_AFS-3216548", "project_ABCDEFG-3216548"]
    },
    {
      "kwargs": {"include_main": False, "include_aux": False},
      "expected": [""]
    },
  ]

  for test in tests:
    assert set(
      re.findall(
        config.Config.symlink_name_regex(**test["kwargs"]),
        "\n".join(test_input),
        flags=re.M
      )
    ) == set(test["expected"])


def test_matches_symlink_regex():
  tests = [
    ["project_DT-1234567", True],
    ["not_a_match", False],
    ["project_peepee", False],
    ["current_project", True],
    ["project_AFS-3216548", True],
    ["project_LONG-32165489", False],
    ["project_ABCDEFG-3216548", True],
  ]

  for test in tests:
    assert config.Config.matches_symlink_regex(test[0]) == test[1]


def test_symlink_name():
  assert config.symlink_name("", is_main=True) == config.symlink_name("asdf", is_main=True)
  assert config.symlink_name("", is_main=True) == config.symlink_name("")
  assert config.symlink_name("T-1234567", is_main=False) != config.symlink_name("T-1234567", is_main=True)
  assert config.symlink_name("Z-7654321", is_main=False).split("_", maxsplit=1)[0] == "project"


def test_prefixes_rules():
  defs = config.Prefixes.definitions()
  assert all(len(key) == 1 for key in defs)
  assert all(key.upper() == key for key in defs)
  assert all(isinstance(info, config.Prefixes.PrefixDescription) for _, info in defs.items())
  assert all(info.short and isinstance(info.short, str) for _, info in defs.items())
  assert all(info.long and isinstance(info.long, str) for _, info in defs.items())

  assert len(defs) == len(config.Prefixes.as_dict())
  json.dumps(config.Prefixes.as_dict())
