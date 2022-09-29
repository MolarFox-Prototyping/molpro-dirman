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


def test_unlink_all_main_only(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = sys_write.unlink_all(main_only=True)
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  
  assert links_before - links_after == {"current_project",}
  assert len(links_before) - 1 == len(links_after)

  assert set(output) == {"current_project",}


def test_unlink_all(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = sys_write.unlink_all(main_only=False)
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])

  assert len(links_before) - 3 == len(links_after)
  assert populated_dir / "home" / "my_custom_symlink_awooo" in links_after
  assert populated_dir / "home" / "ohman_love_documents" in links_after
  assert populated_dir / "home" / "current_project" not in links_after

  assert set(output) == {
    populated_dir / "home" / "current_project",
    populated_dir / "home" / "project_T-1234567",
    populated_dir / "home" / "project_DT-1234567",
  }


def test_unlink_specific_simple(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = sys_write.unlink_specific(populated_dir / "home" / "Projects" / "DT-1234567")
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])

  assert len(links_before) - 1 == len(links_after)
  assert populated_dir / "home" / "project_DT-1234567" not in links_after
  assert populated_dir / "home" / "current_project" in links_after

  assert set(output) == {populated_dir / "home" / "project_DT-1234567",}


def test_unlink_specific_multiple_points(populated_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=populated_dir / "home"
  )
  os.symlink(
    populated_dir / "home" / "Projects" / "DO-4256663",
    populated_dir / "home" / "project_DO-4256663",
    target_is_directory=True
  )
  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = sys_write.unlink_specific(populated_dir / "home" / "Projects" / "DO-4256663")
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])

  assert len(links_before) - 2 == len(links_after)
  assert populated_dir / "home" / "current_project" not in links_after
  assert populated_dir / "home" / "project_DO-4256663" not in links_after

  assert set(output) == {populated_dir / "home" / "current_project", populated_dir / "home" / "project_DO-4256663"}


def test_unlink_specific_nothing_to_remove(structured_dir):
  config.Config.base_symlink_directory = MagicMock(
    return_value=structured_dir / "home"
  )
  links_before = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])
  output = sys_write.unlink_specific(structured_dir / "home" / "Projects" / "DO-4256663")
  links_after = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])

  assert links_before == links_after
  assert output == []