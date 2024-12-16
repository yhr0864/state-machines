from msl.loadlib import Server32
import ctypes


class MyServer(Server32):
    """Wrapper around a 32-bit DLL 'SpecDLL.dll'."""

    def __init__(self, host, port, **kwargs):
        super(MyServer, self).__init__(
            "./devices/uv_vis_lib/dll/SpecDLL.dll", "cdll", host, port
        )

        # Define DLL function signatures
        self.lib.LibTest.restype = ctypes.c_int
        self.lib.LibTest.argtypes = []

        self.lib.version.restype = ctypes.c_char_p
        self.lib.version.argtypes = []

        # Get DLL version
        self.version_str = self.lib.version().decode("utf-8")
        print(f"Loaded SpecDLL version: {self.version_str}")

    def LibTest(self):
        """
        Call the 'LibTest' function in the DLL.
        Returns:
            int: Result from the DLL function.
        """
        print("Calling LibTest from SpecDLL.dll")
        return self.lib.LibTest()

    def version(self):
        """
        Returns the version of the DLL.
        Returns:
            str: Version string from the DLL.
        """
        print("Fetching version from SpecDLL.dll")
        return self.version_str


# Start the server
if __name__ == "__main__":
    server = MyServer("localhost", 8080)
    print("Server is running... Press Ctrl+C to stop.")

    # Blocking loop to keep the server alive
    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server shutting down...")
