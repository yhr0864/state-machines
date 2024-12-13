#include <windows.h>
#include <iostream>

std::string check_dll_architecture_cpp(const std::string& dll_path) {
    HANDLE hFile = CreateFileA(
        dll_path.c_str(),
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    
    if (hFile == INVALID_HANDLE_VALUE) {
        return "Error opening file";
    }
    
    // Read DOS header
    IMAGE_DOS_HEADER dosHeader;
    DWORD bytesRead;
    if (!ReadFile(hFile, &dosHeader, sizeof(IMAGE_DOS_HEADER), &bytesRead, NULL) ||
        bytesRead != sizeof(IMAGE_DOS_HEADER) ||
        dosHeader.e_magic != IMAGE_DOS_SIGNATURE) {
        CloseHandle(hFile);
        return "Invalid DOS header";
    }
    
    // Seek to PE header
    SetFilePointer(hFile, dosHeader.e_lfanew, NULL, FILE_BEGIN);
    
    // Read PE header
    IMAGE_NT_HEADERS peHeader;
    if (!ReadFile(hFile, &peHeader, sizeof(IMAGE_NT_HEADERS), &bytesRead, NULL) ||
        bytesRead != sizeof(IMAGE_NT_HEADERS) ||
        peHeader.Signature != IMAGE_NT_SIGNATURE) {
        CloseHandle(hFile);
        return "Invalid PE header";
    }
    
    CloseHandle(hFile);
    
    // Check machine type
    if (peHeader.FileHeader.Machine == IMAGE_FILE_MACHINE_AMD64) {
        return "64-bit";
    } else if (peHeader.FileHeader.Machine == IMAGE_FILE_MACHINE_I386) {
        return "32-bit";
    } else {
        return "Unknown architecture";
    }
}

std::string result = check_dll_architecture_cpp("./devices/pump_lib/dll/labbCAN_Pump_API.dll");
std::cout << "DLL is " << result << std::endl;