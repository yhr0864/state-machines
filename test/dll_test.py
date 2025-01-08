import pefile
import os


def get_architecture(file_path):
    pe = pefile.PE(file_path)
    machine = pe.FILE_HEADER.Machine
    if machine == 0x014C:
        return "32-bit (x86)"
    elif machine == 0x8664:
        return "64-bit (x64)"
    else:
        return f"Unknown: {hex(machine)}"


exe_path = "U:/projects/devices/syringe pump/CETONI_SDK/capi_analogio_test.exe"

dll_path = "C:/Users/Yu/Downloads/SDK_Multidevices_64bits/SDK_Multidevices_64bits/Sample/SpecDLL.dll"
dll_32_path = "U:/projects/devices/UV Vis/SDK/Sample/SpecDLL.dll"
dll_64_path = "./devices/pump_lib/dll/labbCAN_Bus_API.dll"
print(f"{exe_path} is {get_architecture(exe_path)}")
print(
    f"{dll_path} is {get_architecture(dll_path)}, with size {os.path.getsize(dll_path)}B"
)
print(
    f"{dll_32_path} is {get_architecture(dll_32_path)}, with size {os.path.getsize(dll_32_path)}B"
)
print(
    f"{dll_64_path} is {get_architecture(dll_64_path)}, with size {os.path.getsize(dll_64_path)}B"
)

from ctypes import CDLL

# Load the DLL
example_dll = CDLL(dll_path)
# example_dll_32 = CDLL(dll_32_path)
# dll_64 = CDLL(dll_64_path)

# from msl.loadlib import Server32


# class MyServer(Server32):
#     """Wrapper around a 32-bit C++ library 'my_lib.dll' that has an 'add' and 'version' function."""

#     def __init__(self, host, port, **kwargs):
#         # Load the 'my_lib' shared-library file using ctypes.CDLL
#         super(MyServer, self).__init__(
#             "./devices/uv_vis_lib/dll/SpecDLL.dll", "cdll", host, port
#         )

#         # The Server32 class has a 'lib' property that is a reference to the ctypes.CDLL object

#         # Call the version function from the library
#         self.version = self.lib.version()

#     def LibTest(self):

#         # The shared library's 'add' function takes two integers as inputs and returns the sum
#         return self.lib.LibTest()


# my_server = MyServer("localhost", 8080)
# from msl.loadlib import Client64


# class MyClient(Client64):
#     """Call a function in 'my_lib.dll' via the 'MyServer' wrapper."""

#     def __init__(self):
#         # Specify the name of the Python module to execute on the 32-bit server (i.e., 'my_server')
#         super(MyClient, self).__init__(module32="my_server")

#     def LibTest(self):
#         # The Client64 class has a 'request32' method to send a request to the 32-bit server
#         # Send the 'a' and 'b' arguments to the 'add' method in MyServer
#         return self.request32("Libtest")

#     def version(self):
#         # Get the version
#         return self.request32("version")


# c = MyClient()
# c.LibTest()
