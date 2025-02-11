from .config import *
from .local_read import *
from .local_write import *

core_print = print  # Retain the original print function ptr

from rich import print, print_json
