from msl.loadlib import Client64


class MyClient(Client64):
    """Call a function in 'SpecDLL.dll' via the 'MyServer' wrapper."""

    def __init__(self):
        # Connect to the 32-bit server running 'MyServer'
        super(MyClient, self).__init__(module32="my_server")

    def LibTest(self):
        """Call the 'LibTest' function via the server."""
        return self.request32("LibTest")

    def get_version(self):
        """Get the DLL version via the server."""
        return self.request32("version")


c = MyClient()

# Test the 'LibTest' function
result = c.LibTest()
print("LibTest result:", result)

# Get the library version
version = c.get_version()
print("DLL version:", version)
