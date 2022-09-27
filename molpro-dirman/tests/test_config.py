# Test config methods
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
