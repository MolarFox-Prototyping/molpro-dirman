
import re
import json

from .config import *
from .sys_read import *
from .sys_write import *

RICH_ENABLED = None

# Try importing rich, overriding the stock print function if able
try:
  import rich
  RICH_ENABLED = True
except ModuleNotFoundError:
  RICH_ENABLED = False

core_print = print  # Retain the original print function ptr

def print(*args, **kwargs) -> None:
  "Print with rich, or strip rich formatting and print with vanilla print"
  if RICH_ENABLED:
    return rich.print(*args, **kwargs)
  return core_print(  
    *[re.sub("\[.*?\]","",s) for s in args],  # Strip away rich's formatting
    **kwargs
  )


def print_json(*args, **kwargs) -> None:
  "Print with rich's fancy json output, or use regular json dumps otherwise"
  if RICH_ENABLED:
    return rich.print_json(*args, **kwargs)
  if "data" in kwargs:
    print(
      json.dumps(kwargs["data"], indent=kwargs.get("indent", 2))
    )
  else:
    print(kwargs.get("json", args[0]))
