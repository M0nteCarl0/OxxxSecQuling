# ⚡️ 📡 IoT & Embedded Router Firmware Emulation: NVRAM Mocking (Python practice)

Emulating embedded Linux firmware (such as router `httpd` web servers, UPnP services, or telemetry daemons) is notoriously difficult. On physical devices, these binaries rely heavily on non-volatile RAM (NVRAM) APIs (`nvram_get`, `nvram_set`, `nvram_bufget`) and vendor hardware interfaces. When executed outside the physical router SoC, the binaries crash immediately due to missing NVRAM daemons or broken IPC pipes. Qiling solves this by allowing analysts to hook vendor C library APIs and provide dynamic in-memory dictionary-backed NVRAM responses.

## 🧠 Core Concept
- **Vendor API Hooking**: Intercept embedded router C library functions (`libnvram.so`, `libshared.so`) before they query missing kernel drivers.
- **In-Memory NVRAM Registry**: Maintain an in-memory key-value dictionary in Python to simulate router settings (SSID, admin credentials, LAN IP, firewall status).
- **Automated Parameter Extraction**: Extract requested NVRAM keys from function argument registers (`$a0` on MIPS, `r0` on ARM) dynamically.
- **Dynamic Memory Allocation for Strings**: Allocate small guest memory buffers to return string values for requested configuration keys.
- **Daemon Stabilization**: Prevent premature binary crashes and allow embedded web servers or background daemons to initialize completely.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Dynamic vulnerability research and 1-day/0-day bug hunting in IoT router web interfaces.
- Emulating UPnP daemons (`miniupnpd`) and router management services without physical hardware.
- Fuzzing embedded parsing routines that rely on pre-populated configuration parameters.
- Analyzing malicious Mirai / Mozi IoT botnet variants interacting with local router daemons.
- Automating firmware security compliance and credential audits in continuous testing pipelines.

## ⚠️ Caveats & Responsible Practice
- **Memory Leaks in Repeated Queries**: If `nvram_get` is called millions of times in a loop, reuse a static buffer table instead of calling `ql.os.heap.alloc` on every invocation.
- **Architecture Endianness**: MIPS binaries are frequently Big-Endian (`MIPS32`) or Little-Endian (`MIPS32EL`); ensure your `QL_ARCH` match.
- **Socket & Pipe Dependencies**: Many IoT daemons communicate over UNIX domain sockets (`/var/run/nvram.sock`); combine API hooks with VFS mocking if needed.
- **Stripped Binaries**: If `libnvram` is statically linked and stripped, find the function address via Ghidra/IDA and use `ql.hook_address()`.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [MIPS32EL Router Firmware RootFS](https://github.com/qilingframework/rootfs/tree/master/mips32el_linux)
- **Router Daemons & NVRAM Binaries**: [Qiling Router Examples](https://github.com/qilingframework/qiling/tree/master/examples/rootfs/mips32el_linux)
- **NVRAM Virtualization Guide**: [Qiling IoT Emulation Examples](https://github.com/qilingframework/qiling/tree/master/examples)
## 🔗 Resources
- Qiling IoT Emulation Examples (https://github.com/qilingframework/qiling/tree/master/examples)
- Firmware Analysis Toolkit (https://github.com/attify/firmware-analysis-toolkit)

#Qiling #IoT #FirmwareSecurity #MIPS #ReverseEngineering #NVRAM #EmbeddedSecurity #CyberSecurity
