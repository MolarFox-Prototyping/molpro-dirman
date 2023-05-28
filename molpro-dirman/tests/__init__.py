import importlib

main = importlib.import_module("molpro_dirman.__main__")
config = importlib.import_module("molpro_dirman.config")
sys_read = importlib.import_module("molpro_dirman.sys_read")
sys_write = importlib.import_module("molpro_dirman.sys_write")