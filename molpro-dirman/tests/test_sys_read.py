# Test passive system interaction methods

from datetime import datetime
from . import sys_read
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
