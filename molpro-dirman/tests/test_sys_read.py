# Test passive system interaction methods

# import importlib

# sys_read = importlib.import_module("molpro-dirman.sys_read")
from tests.fixtures import populated_dir, structured_dir, generate_data

def test_ls_dirs_only(populated_dir):
  for key in (populated_dir / "home" / "Projects" / "T-1234567").iterdir():
    print(key)
  raise Exception