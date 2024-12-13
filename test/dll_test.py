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


dll_path = "./devices/uv_vis_lib/dll/SpecDLL.dll"
print(f"{dll_path} is {get_architecture(dll_path)}")
