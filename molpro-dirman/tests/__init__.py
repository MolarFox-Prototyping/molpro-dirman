import importlib

main = importlib.import_module("molpro_dirman.__main__")
config = importlib.import_module("molpro_dirman.config")
local_read = importlib.import_module("molpro_dirman.local_read")
local_write = importlib.import_module("molpro_dirman.local_write")