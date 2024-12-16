import pefile


def get_architecture(file_path):
    pe = pefile.PE(file_path)
    machine = pe.FILE_HEADER.Machine
    if machine == 0x014C:
        return "32-bit (x86)"
    elif machine == 0x8664:
        return "64-bit (x64)"
    else:
        return f"Unknown: {hex(machine)}"


# dll_path = "./devices/uv_vis_lib/dll/SpecDLL.dll"
# print(f"{dll_path} is {get_architecture(dll_path)}")

from msl.loadlib import Server32


class MyServer(Server32):
    """Wrapper around a 32-bit C++ library 'my_lib.dll' that has an 'add' and 'version' function."""

    def __init__(self, host, port, **kwargs):
        # Load the 'my_lib' shared-library file using ctypes.CDLL
        super(MyServer, self).__init__(
            "./devices/uv_vis_lib/dll/SpecDLL.dll", "cdll", host, port
        )

        # The Server32 class has a 'lib' property that is a reference to the ctypes.CDLL object

        # Call the version function from the library
        self.version = self.lib.version()

    def LibTest(self):

        # The shared library's 'add' function takes two integers as inputs and returns the sum
        return self.lib.LibTest()


my_server = MyServer("localhost", 8080)
from msl.loadlib import Client64


class MyClient(Client64):
    """Call a function in 'my_lib.dll' via the 'MyServer' wrapper."""

    def __init__(self):
        # Specify the name of the Python module to execute on the 32-bit server (i.e., 'my_server')
        super(MyClient, self).__init__(module32="my_server")

    def LibTest(self):
        # The Client64 class has a 'request32' method to send a request to the 32-bit server
        # Send the 'a' and 'b' arguments to the 'add' method in MyServer
        return self.request32("Libtest")

    def version(self):
        # Get the version
        return self.request32("version")


c = MyClient()
c.LibTest()
