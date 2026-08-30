#!/usr/bin/env python3
"""
Post 19: macOS Mach-O Binary Emulation & Apple LibSystem Interception
Emulating an ARM64/x86_64 macOS CLI binary, hooking `sysctlbyname` and inspecting security parameters.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

def hook_sysctlbyname(ql: Qiling) -> int:
    name_ptr = ql.os.function_arg(0)
    oldp_ptr = ql.os.function_arg(1)
    oldlenp_ptr = ql.os.function_arg(2)
    
    # Read queried sysctl property string
    query_name = ql.os.utils.read_cstring(name_ptr)
    print(f"[MACOS API] sysctlbyname(name='{query_name}')")
    
    # If binary is querying hardware model or security flags
    if "hw.model" in query_name:
        fake_model = b"MacBookPro18,1\x00"
        if oldp_ptr != 0:
            ql.mem.write(oldp_ptr, fake_model)
        return 0 # KERN_SUCCESS
    elif "kern.osversion" in query_name:
        fake_ver = b"21G115\x00"
        if oldp_ptr != 0:
            ql.mem.write(oldp_ptr, fake_ver)
        return 0
        
    return 0

def run_macho_sandbox(macho_binary: str, rootfs_path: str) -> None:
    print(f"[*] Initializing macOS Mach-O Sandbox for {macho_binary}...")
    ql = Qiling(
        argv=[macho_binary],
        rootfs=rootfs_path,
        ostype=QL_OS.MACOS,
        archtype=QL_ARCH.X8664,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Intercept Apple LibSystem APIs
    ql.os.set_api("sysctlbyname", hook_sysctlbyname)
    
    print("[*] Emulating macOS Mach-O execution...")
    try:
        ql.run()
    except Exception as err:
        print(f"[-] Mach-O execution ended: {err}")

if __name__ == "__main__":
    TARGET_MACHO = "rootfs/x8664_macos/bin/macho_security_checker"
    ROOTFS_MACOS = "rootfs/x8664_macos"
    run_macho_sandbox(TARGET_MACHO, ROOTFS_MACOS)
