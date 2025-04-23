# Test active system interaction methods

from unittest.mock import MagicMock

from . import local_write, config
from tests.fixtures import *

def test_delete_symlink(populated_dir):
  with pytest.raises(ValueError):
    local_write.delete_symlink(populated_dir / "home" / "Projects" / "T-1234567" / "README.md")

  with pytest.raises(ValueError):
    local_write.delete_symlink(populated_dir / "home" / "Documents")

  with pytest.raises(ValueError):
    local_write.delete_symlink(populated_dir / "home" / "my_custom_symlink_awooo")

  assert (populated_dir / "home" / "my_custom_symlink_awooo").exists()

  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.delete_symlink(populated_dir / "home" / "my_custom_symlink_awooo", mpdman_only=False)
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])

  assert not (populated_dir / "home" / "my_custom_symlink_awooo").exists()
  assert output == populated_dir / "home" / "my_custom_symlink_awooo"
  assert links_before - links_after == {populated_dir / "home" / "my_custom_symlink_awooo",}
  assert len(links_before) -1 == len(links_after)
  


def test_move_main_to_aux_simple(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)
  
  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  aux_link = populated_dir / "home" / config.symlink_name("DO-4256663", is_main=False)
  tgt_project = populated_dir / "home" / "Projects" / "DO-4256663"

  assert Path(os.readlink(main_link)) == tgt_project
  assert not aux_link.exists()

  output = local_write.move_main_to_aux()

  assert output == aux_link
  assert aux_link.exists()
  assert Path(os.readlink(aux_link)) == tgt_project
  assert not main_link.exists()


def test_move_main_to_aux_non_existent(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  os.remove(main_link)
  assert not main_link.exists()

  with pytest.raises(FileNotFoundError):
    local_write.move_main_to_aux()


def test_move_main_to_aux_already_existing(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  aux_link = populated_dir / "home" / config.symlink_name("DO-4256663", is_main=False)
  tgt_project = populated_dir / "home" / "Projects" / "DO-4256663"

  os.symlink(os.readlink(main_link), aux_link, target_is_directory=True)
  assert main_link.exists()
  assert aux_link.exists()
  assert Path(os.readlink(main_link)) == Path(os.readlink(aux_link)) == tgt_project

  output = local_write.move_main_to_aux()

  assert output == aux_link
  assert aux_link.exists()
  assert Path(os.readlink(aux_link)) == tgt_project
  assert not main_link.exists()


def test_move_main_to_aux_linked_elsewhere(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  main_link = populated_dir / "home" / config.Config.main_project_symlink_name()
  aux_link = populated_dir / "home" / config.symlink_name("DO-4256663", is_main=False)
  tgt_project = populated_dir / "home" / "Projects" / "DO-4256663"

  os.symlink(populated_dir / "home" / "Documents", aux_link, target_is_directory=True)
  assert main_link.exists()
  assert aux_link.exists()
  assert Path(os.readlink(main_link)) == tgt_project
  assert Path(os.readlink(aux_link)) != tgt_project

  with pytest.raises(local_write.ProjectSymLinkExists):
    local_write.move_main_to_aux()
  
  output = local_write.move_main_to_aux(overwrite_existing=True)

  assert output == aux_link
  assert aux_link.exists()
  assert Path(os.readlink(aux_link)) == tgt_project
  assert not main_link.exists()


def test_unlink_main_only(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.unlink_main()
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  
  assert links_before - links_after == {populated_dir / "home" / "current_project",}
  assert len(links_before) - 1 == len(links_after)

  assert set(output) == {populated_dir / "home" / "current_project"}


def test_unlink_all(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.unlink_all()
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


def test_unlink_specific_simple(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)
  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.unlink_specific(populated_dir / "home" / "Projects" / "DT-1234567")
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])

  assert len(links_before) - 1 == len(links_after)
  assert populated_dir / "home" / "project_DT-1234567" not in links_after
  assert populated_dir / "home" / "current_project" in links_after

  assert set(output) == {populated_dir / "home" / "project_DT-1234567",}


def test_unlink_specific_multiple_points(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)
  os.symlink(
    populated_dir / "home" / "Projects" / "DO-4256663",
    populated_dir / "home" / "project_DO-4256663",
    target_is_directory=True
  )
  links_before = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.unlink_specific(populated_dir / "home" / "Projects" / "DO-4256663")
  links_after = set([k for k in (populated_dir / "home").iterdir() if os.path.islink(k)])

  assert len(links_before) - 2 == len(links_after)
  assert populated_dir / "home" / "current_project" not in links_after
  assert populated_dir / "home" / "project_DO-4256663" not in links_after

  assert set(output) == {populated_dir / "home" / "current_project", populated_dir / "home" / "project_DO-4256663"}


def test_unlink_specific_nothing_to_remove(structured_dir, mock_base_directories):
  mock_base_directories(structured_dir)

  links_before = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.unlink_specific(structured_dir / "home" / "Projects" / "DO-4256663")
  links_after = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])

  assert links_before == links_after
  assert output == []


def test_symlink_project_simple(structured_dir, mock_base_directories):
  mock_base_directories(structured_dir)

  links_before = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.symlink_project(structured_dir / "home" / "Projects" / "DO-4256663", is_main=True)
  links_after = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])

  assert not links_before
  assert links_after == {structured_dir / "home" / "current_project",}
  assert output == structured_dir / "home" / "current_project"


def test_symlink_project_simple_aux(structured_dir, mock_base_directories):
  mock_base_directories(structured_dir)

  links_before = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])
  output = local_write.symlink_project(structured_dir / "home" / "Projects" / "DO-4256663", is_main=False)
  links_after = set([k for k in (structured_dir / "home").iterdir() if os.path.islink(k)])

  assert not links_before
  assert links_after == {structured_dir / "home" / "project_DO-4256663",}
  assert output == structured_dir / "home" / "project_DO-4256663"


def test_symlink_project_invalid_paths(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  with pytest.raises(local_write.ProjectSymLinkFailure):
    local_write.symlink_project(populated_dir / "home" / "Documents", True)

  with pytest.raises(local_write.ProjectSymLinkFailure):
    local_write.symlink_project(populated_dir / "home" / "Documents", False)

  with pytest.raises(local_write.ProjectSymLinkExists):
    local_write.symlink_project(populated_dir / "home" / "Projects" / "T-1234567" / "README.md", True)

  local_write.symlink_project(populated_dir / "home" / "Projects" / "T-1234567" / "README.md", False)


def test_symlink_project_already_created(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  with pytest.raises(local_write.ProjectAlreadySymLinked):
    local_write.symlink_project(populated_dir / "home" / "Projects" / "DO-4256663", True)

  with pytest.raises(local_write.ProjectAlreadySymLinked):
    local_write.symlink_project(populated_dir / "home" / "Projects" / "T-1234567", False)


def test_symlink_project_overwrite_existing(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  os.symlink(
    populated_dir / "home" / "OtherFolder", 
    populated_dir / "home" / "project_APJ-1234567", 
    target_is_directory=True
  )

  with pytest.raises(local_write.ProjectSymLinkExists):
    local_write.symlink_project(populated_dir / "home" / "Projects" / "APJ-1234567", False)

  old_main = os.readlink(populated_dir / "home" / "current_project")
  assert Path(os.readlink(populated_dir / "home" / "project_APJ-1234567")) == populated_dir / "home" / "OtherFolder"
  
  output = local_write.symlink_project(populated_dir / "home" / "Projects" / "APJ-1234567", False, overwrite=True)
  
  assert Path(os.readlink(populated_dir / "home" / "project_APJ-1234567")) == populated_dir / "home" / "Projects" / "APJ-1234567"
  assert output == populated_dir / "home" / "project_APJ-1234567"
  assert old_main == os.readlink(populated_dir / "home" / "current_project")


def test_symlink_project_overwrite_existing_main(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  with pytest.raises(local_write.ProjectSymLinkExists):
    local_write.symlink_project(populated_dir / "home" / "Projects" / "APJ-1234567", True)

  old_main = os.readlink(populated_dir / "home" / "current_project")
  assert Path(os.readlink(populated_dir / "home" / "current_project")) != populated_dir / "home" / "Projects" / "APJ-1234567"

  output = local_write.symlink_project(
    populated_dir / "home" / "Projects" / "APJ-1234567", 
    True, 
    overwrite=True,
    keep_old_main=False
  )

  assert Path(os.readlink(populated_dir / "home" / "current_project")) == populated_dir / "home" / "Projects" / "APJ-1234567"
  assert output == populated_dir / "home" / "current_project"
  assert old_main != os.readlink(populated_dir / "home" / "current_project")  
  assert not (populated_dir / "home" / f"project_{Path(old_main).parts[-1]}").exists()


def test_symlink_project_overwrite_existing_main_retain(populated_dir, mock_base_directories):
  mock_base_directories(populated_dir)

  with pytest.raises(local_write.ProjectSymLinkExists):
    local_write.symlink_project(populated_dir / "home" / "Projects" / "APJ-1234567", True)

  old_main = os.readlink(populated_dir / "home" / "current_project")
  assert Path(os.readlink(populated_dir / "home" / "current_project")) != populated_dir / "home" / "Projects" / "APJ-1234567"

  output = local_write.symlink_project(
    populated_dir / "home" / "Projects" / "APJ-1234567", 
    True, 
    overwrite=True,
    keep_old_main=True
  )

  assert Path(os.readlink(populated_dir / "home" / "current_project")) == populated_dir / "home" / "Projects" / "APJ-1234567"
  assert output == populated_dir / "home" / "current_project"
  assert old_main != os.readlink(populated_dir / "home" / "current_project")  
  assert (populated_dir / "home" / f"project_{Path(old_main).parts[-1]}").exists()


def test_symlink_project_exists_elsewhere(structured_dir, mock_base_directories):
  mock_base_directories(structured_dir)

  main_link = structured_dir / "home" / config.Config.main_project_symlink_name()
  aux_link = structured_dir / "home" / config.symlink_name("APJ-1234567", is_main=False)
  tgt_project = structured_dir / "home" / "Projects" / "APJ-1234567"

  def all_links_in_home() -> list[Path]:
    return [k for k in (structured_dir / "home").iterdir() if os.path.islink(k)]

  assert all_links_in_home() == []
  local_write.symlink_project(tgt_project, True)
  assert all_links_in_home() == [main_link]

  with pytest.raises(local_write.ProjectAlreadySymLinked):
    local_write.symlink_project(tgt_project, True)

  assert all_links_in_home() == [main_link]

  output = local_write.symlink_project(tgt_project, False)

  assert output == aux_link
  assert set(all_links_in_home()) == {main_link, aux_link}

  assert all(
    Path(os.readlink(ln)) == tgt_project for ln in 
    all_links_in_home()
  )


def test_create_project(structured_dir, mock_base_directories):
  def projects_in_local(path: Path) -> list[str]:
    return [k.parts[-1] for k in (path / "home" / "Projects").iterdir() if k.is_dir()]

  mock_base_directories(structured_dir)
  assert "S-1234567" not in projects_in_local(structured_dir)
  new_project_path = local_write.create_project(['S'], "A test project", "Wow! A description", serial=1234567)
  assert "S-1234567" in projects_in_local(structured_dir)

  assert new_project_path == structured_dir / "home" / "Projects" / "S-1234567"

  assert open(structured_dir / "home" / "Projects" / "S-1234567" / "README.md", "r").read() == "# A test project\n## S-1234567\n\nWow! A description"


def test_create_project_already_exists(structured_dir, mock_base_directories):
  mock_base_directories(structured_dir)
  with pytest.raises(local_write.ProjectAlreadyExists):
    local_write.create_project(['T'], "A pre-existing project", "This should fail, huh?", serial=1234567)
