#!/usr/bin/env python3
"""
Post 03: Precision Memory Mapping, Injection, and Struct Layout
Mapping a custom memory segment, injecting a mock C structure, and preparing execution for an isolated function.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import struct

def setup_isolated_memory_context() -> None:
    # Initialize bare-metal ARM64 context
    ql = Qiling(
        argv=["rootfs/arm64_linux/bin/crypto_lib.so"],
        rootfs="rootfs/arm64_linux",
        ostype=QL_OS.LINUX,
        archtype=QL_ARCH.ARM64,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # 1. Map custom memory region for input/output buffers: Base 0x70000000, Size 64KB
    CUSTOM_BASE = 0x70000000
    CUSTOM_SIZE = 0x10000 # 64 KB (must be page-aligned 4096)
    
    ql.mem.map(CUSTOM_BASE, CUSTOM_SIZE, info="[Custom_Payload_Region]")
    
    # 2. Build a mock C struct:
    # struct session_data { uint32_t session_id; uint32_t payload_len; char key[16]; char data[32]; };
    session_id = 0x1337BEEF
    key = b"A" * 16
    data = b"SecretMessagePayloadToDecrypt123"
    payload_len = len(data)
    
    struct_format = "<II16s32s"
    packed_struct = struct.pack(struct_format, session_id, payload_len, key, data)
    
    # Write packed structure into our custom mapped memory
    struct_addr = CUSTOM_BASE + 0x100
    ql.mem.write(struct_addr, packed_struct)
    print(f"[+] Injected structure at 0x{struct_addr:08x} ({len(packed_struct)} bytes)")
    
    # 3. Setup CPU registers to pass the structure pointer to target function
    ql.arch.regs.x0 = struct_addr # First argument in ARM64 ABI
    
    # 4. Inspect current memory map
    print("[*] Current Guest Memory Map:")
    ql.mem.show_map()

if __name__ == "__main__":
    setup_isolated_memory_context()
