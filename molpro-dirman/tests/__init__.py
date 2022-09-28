import pytest
import importlib

main = importlib.import_module("molpro-dirman.__main__")
config = importlib.import_module("molpro-dirman.config")
sys_read = importlib.import_module("molpro-dirman.sys_read")
sys_write = importlib.import_module("molpro-dirman.sys_write")