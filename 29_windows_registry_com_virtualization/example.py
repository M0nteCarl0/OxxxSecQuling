#!/usr/bin/env python3
"""
Post 29: Windows Registry & COM Virtualization Deep Dive
Sandboxing a Windows dropper, logging all registry `Run` key writes and COM object invocations.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# In-memory log of suspicious persistence activities
persistence_log = []

def hook_RegSetValueExW(ql: Qiling) -> int:
    hKey = ql.os.function_arg(0)
    lpValueName_ptr = ql.os.function_arg(1)
    Reserved = ql.os.function_arg(2)
    dwType = ql.os.function_arg(3)
    lpData_ptr = ql.os.function_arg(4)
    cbData = ql.os.function_arg(5)
    
    val_name = ql.os.utils.read_wstring(lpValueName_ptr)
    # Read payload data written to registry
    data_bytes = ql.mem.read(lpData_ptr, cbData)
    
    print("=" * 60)
    print(f"[!] REGISTRY WRITE DETECTED: RegSetValueExW")
    print(f"    Value Name : '{val_name}'")
    print(f"    Data Type  : 0x{dwType:x}")
    print(f"    Data Value : {data_bytes.hex()} (ASCII: {data_bytes})")
    print("=" * 60)
    
    persistence_log.append({"val_name": val_name, "data": data_bytes})
    return 0 # ERROR_SUCCESS

def hook_CoCreateInstance(ql: Qiling) -> int:
    rclsid_ptr = ql.os.function_arg(0)
    pUnkOuter = ql.os.function_arg(1)
    dwClsContext = ql.os.function_arg(2)
    riid_ptr = ql.os.function_arg(3)
    ppv_ptr = ql.os.function_arg(4)
    
    clsid_raw = ql.mem.read(rclsid_ptr, 16)
    print(f"[COM INTERFACE] CoCreateInstance requested CLSID: {clsid_raw.hex()}")
    # S_OK = 0
    return 0

def run_win_registry_sandbox(pe_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Windows Registry Sandbox for {pe_path}...")
    ql = Qiling([pe_path], rootfs_path, ostype=QL_OS.WINDOWS, archtype=QL_ARCH.X86, verbose=QL_VERBOSE.DEFAULT)
    
    # Hook Windows Registry and COM APIs
    ql.os.set_api("RegSetValueExW", hook_RegSetValueExW)
    ql.os.set_api("CoCreateInstance", hook_CoCreateInstance)
    
    print("[*] Running malware to capture registry modifications...")
    try:
        ql.run()
    except Exception:
        pass
        
    print(f"[+] Analysis Complete: Captured {len(persistence_log)} persistence registry event(s).")

if __name__ == "__main__":
    TARGET = "rootfs/x86_windows/bin/persistence_dropper.exe"
    ROOTFS = "rootfs/x86_windows"
    run_win_registry_sandbox(TARGET, ROOTFS)
