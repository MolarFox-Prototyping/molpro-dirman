
import re

from .config import *
from .sys_read import *
from .sys_write import *

RICH_ENABLED = None

# Try importing rich, overriding the stock print function if able
try:
  from rich import print
  RICH_ENABLED = True
except ModuleNotFoundError:
  RICH_ENABLED = False

core_print = print  # Retain the original print function ptr

def print(*args, **kwargs) -> None:
  "Print with rich, or strip rich formatting and print with vanilla print"
  if RICH_ENABLED:
    return core_print(*args, **kwargs)
  return core_print(  
    *[re.sub("\[.*?\]","",s) for s in args],  # Strip away rich's formatting
    **kwargs
  )
