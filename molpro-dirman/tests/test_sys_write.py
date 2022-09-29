# Test active system interaction methods

from unittest.mock import MagicMock

from . import sys_write, config
from tests.fixtures import *

def test_move_main_to_aux_simple(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  aux_link = populated_dir / "home" / config.symlink_name("DO-4256663", is_main=False)
  tgt_project = populated_dir / "home" / "Projects" / "DO-4256663"

  assert Path(os.readlink(main_link)) == tgt_project
  assert not aux_link.exists()

  output = sys_write.move_main_to_aux()

  assert output == aux_link
  assert aux_link.exists()
  assert Path(os.readlink(aux_link)) == tgt_project
  assert not main_link.exists()


def test_move_main_to_aux_non_existent(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  os.remove(main_link)
  assert not main_link.exists()

  with pytest.raises(FileNotFoundError):
    sys_write.move_main_to_aux()


def test_move_main_to_aux_already_existing(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  aux_link = populated_dir / "home" / config.symlink_name("DO-4256663", is_main=False)
  tgt_project = populated_dir / "home" / "Projects" / "DO-4256663"

  os.symlink(os.readlink(main_link), aux_link, target_is_directory=True)
  assert main_link.exists()
  assert aux_link.exists()
  assert Path(os.readlink(main_link)) == Path(os.readlink(aux_link)) == tgt_project

  output = sys_write.move_main_to_aux()

  assert output == aux_link
  assert aux_link.exists()
  assert Path(os.readlink(aux_link)) == tgt_project
  assert not main_link.exists()


def test_move_main_to_aux_linked_elsewhere(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  aux_link = populated_dir / "home" / config.symlink_name("DO-4256663", is_main=False)
  tgt_project = populated_dir / "home" / "Projects" / "DO-4256663"

  os.symlink(populated_dir / "home" / "Documents", aux_link, target_is_directory=True)
  assert main_link.exists()
  assert aux_link.exists()
  assert Path(os.readlink(main_link)) == tgt_project
  assert Path(os.readlink(aux_link)) != tgt_project

  with pytest.raises(sys_write.ProjectSymLinkExists):
    sys_write.move_main_to_aux()
  
  output = sys_write.move_main_to_aux(overwrite_existing=True)

  assert output == aux_link
  assert aux_link.exists()
  assert Path(os.readlink(aux_link)) == tgt_project
  assert not main_link.exists()
