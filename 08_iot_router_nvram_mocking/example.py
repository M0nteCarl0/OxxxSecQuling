#!/usr/bin/env python3
"""
Post 08: IoT & Embedded Router Firmware Emulation (NVRAM Mocking)
Emulating a MIPS router `httpd` binary and mocking `nvram_get` / `nvram_set` C APIs via `ql.os.set_api`.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# In-memory dictionary representing router non-volatile configuration
VIRTUAL_NVRAM = {
    "http_username": "admin",
    "http_passwd": "SuperSecretPassword123!",
    "lan_ipaddr": "192.168.1.1",
    "lan_netmask": "255.255.255.0",
    "wlan0_ssid": "SecureRouter_Corporate",
    "wl0_security_mode": "wpa2_personal",
    "system_ready": "1"
}

def hook_nvram_get(ql: Qiling) -> int:
    key_ptr = ql.os.function_arg(0)
    key_name = ql.os.utils.read_cstring(key_ptr)
    
    if key_name in VIRTUAL_NVRAM:
        val = VIRTUAL_NVRAM[key_name]
        print(f"[NVRAM] nvram_get('{key_name}') -> '{val}'")
        # Allocate guest memory for string and return pointer
        val_bytes = val.encode() + b"\x00"
        ret_addr = ql.os.heap.alloc(len(val_bytes))
        ql.mem.write(ret_addr, val_bytes)
        return ret_addr
    else:
        print(f"[NVRAM] nvram_get('{key_name}') -> NOT FOUND (returning NULL)")
        return 0 # NULL pointer

def hook_nvram_set(ql: Qiling) -> int:
    key_ptr = ql.os.function_arg(0)
    val_ptr = ql.os.function_arg(1)
    
    key_name = ql.os.utils.read_cstring(key_ptr)
    val_str = ql.os.utils.read_cstring(val_ptr)
    print(f"[NVRAM] nvram_set('{key_name}', '{val_str}')")
    
    VIRTUAL_NVRAM[key_name] = val_str
    return 0 # 0 indicates SUCCESS in standard libnvram

def run_iot_emulation(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing IoT MIPS router sandbox for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.MIPS, verbose=QL_VERBOSE.DEFAULT)
    
    # Hook vendor NVRAM library functions
    ql.os.set_api("nvram_get", hook_nvram_get)
    ql.os.set_api("nvram_set", hook_nvram_set)
    ql.os.set_api("nvram_safe_get", hook_nvram_get)
    
    print("[*] Starting embedded binary emulation with virtualized NVRAM...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/mips32el_linux/bin/router_httpd"
    ROOTFS = "rootfs/mips32el_linux"
    run_iot_emulation(TARGET, ROOTFS)
