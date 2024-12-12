"""
This file refers to cetoni qmixsdk, but simplified
"""

import sys
import os
import ctypes
from ctypes import util


def load_lib(libname):
    """
    Helper function for loading UvvisSDK DLLs.
    This helper function ensures that DLL loading works for all Python 3
    versions
    """

    libpath = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../dll"))

    libname = os.path.join(libpath, libname + ".dll")
    # We need to extend that library search path only once, so we do it
    # only for the first call here

    # From python 3.8 on loading DLLs from folder in PATH environment
    # does not work anymore. We use os.add_dll_directory instead
    if sys.version_info >= (3, 8):
        os.add_dll_directory(libpath)
    else:
        sys.path.append(libpath)
        os.environ["PATH"] = libpath + os.pathsep + os.environ["PATH"]

    print(libname)
    return ctypes.windll.LoadLibrary(libname)


if __name__ == "__main__":
    load_lib("SpecDLL")
    print(os.path.abspath(os.path.join(os.path.dirname(__file__), r"../dll")))
