#!/usr/bin/env python3
"""
Post 12: UEFI DXE & SMM Firmware Emulation & Vulnerability Research
Loading an extracted UEFI `.efi` driver module, hooking `LocateProtocol` and `GetVariable`.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Mock UEFI NVRAM variables storage
MOCK_UEFI_NVRAM = {
    "AdminPasswordAuth": b"\x01\x00\x00\x00\xDE\xAD\xBE\xEF",
    "SecureBootSetup": b"\x01",
    "CustomSecurityConfig": b"A" * 64
}

def hook_uefi_GetVariable(ql: Qiling) -> int:
    var_name_ptr = ql.os.function_arg(0)
    vendor_guid_ptr = ql.os.function_arg(1)
    attributes_ptr = ql.os.function_arg(2)
    data_size_ptr = ql.os.function_arg(3)
    data_buf_ptr = ql.os.function_arg(4)
    
    # Read UTF-16LE variable name
    var_name = ql.os.utils.read_wstring(var_name_ptr)
    print(f"[UEFI EFI_GET_VARIABLE] Querying variable: '{var_name}'")
    
    if var_name in MOCK_UEFI_NVRAM:
        val = MOCK_UEFI_NVRAM[var_name]
        # Write mock variable data into guest buffer
        ql.mem.write(data_buf_ptr, val)
        # EFI_SUCCESS = 0
        return 0
    else:
        print(f"  [-] Variable '{var_name}' not found -> EFI_NOT_FOUND (0x8000000e)")
        # EFI_NOT_FOUND = 0x800000000000000E (64-bit EFI status)
        return 0x800000000000000E

def run_uefi_sandbox(efi_driver_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing UEFI DXE Driver Sandbox for {efi_driver_path}...")
    ql = Qiling(
        argv=[efi_driver_path],
        rootfs=rootfs_path,
        ostype=QL_OS.UEFI,
        archtype=QL_ARCH.X8664,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Intercept UEFI Runtime Service: GetVariable
    ql.os.set_api("GetVariable", hook_uefi_GetVariable)
    
    print("[*] Starting UEFI driver execution...")
    try:
        ql.run()
    except Exception as err:
        print(f"[*] Driver execution completed or yielded: {err}")

if __name__ == "__main__":
    TARGET_EFI = "rootfs/x8664_efi/bin/SampleDxeDriver.efi"
    ROOTFS_EFI = "rootfs/x8664_efi"
    run_uefi_sandbox(TARGET_EFI, ROOTFS_EFI)
