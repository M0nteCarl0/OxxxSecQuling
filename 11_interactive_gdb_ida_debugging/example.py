#!/usr/bin/env python3
"""
Post 11: Interactive Remote Debugging with GDB & IDA Pro Remote Stub
Launching Qiling with an embedded GDB server stub and attaching IDA Pro or GDB-multiarch.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import threading
import time

def start_debug_session(binary_path: str, rootfs_path: str, port: int = 9999) -> None:
    print(f"[*] Initializing Qiling sandbox for {binary_path}...")
    ql = Qiling(
        argv=[binary_path],
        rootfs=rootfs_path,
        ostype=QL_OS.LINUX,
        archtype=QL_ARCH.ARM,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # 1. Configure embedded GDB remote stub
    # Format: "gdb:IP:PORT" or "qndb" for Qiling's native terminal debugger
    debug_listen = f"127.0.0.1:{port}"
    ql.debugger = f"gdb:{debug_listen}"
    
    print("=" * 65)
    print(f"[+] GDB Remote Debugger listening on: {debug_listen}")
    print("[+] How to connect:")
    print(f"    GDB CLI : gdb-multiarch -ex 'target remote {debug_listen}'")
    print(f"    IDA Pro : Select 'Remote GDB Debugger' -> Host: 127.0.0.1 Port: {port}")
    print(f"    Ghidra  : In Debugger tool -> Connect to GDB via RSP target")
    print("=" * 65)
    
    # 2. Run emulation (Qiling will pause at entry point waiting for GDB connection)
    print("[*] Waiting for debugger connection...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/arm_linux/bin/arm_crypto_challenge"
    ROOTFS = "rootfs/arm_linux"
    start_debug_session(TARGET, ROOTFS, port=9999)
