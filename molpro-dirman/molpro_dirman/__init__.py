from .config import *
from .sys_read import *
from .sys_write import *

core_print = print  # Retain the original print function ptr

from rich import print, print_json
