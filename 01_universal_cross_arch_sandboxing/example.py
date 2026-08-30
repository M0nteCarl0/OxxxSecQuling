#!/usr/bin/env python3
"""
Post 01: Universal Cross-Architecture Binary Sandboxing
Loading an ARM Linux ELF binary on an x86_64 host with custom rootfs and capturing execution output.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import sys
import io

def run_cross_arch_sandbox(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Qiling sandbox for {binary_path}...")
    
    # Qiling automatically detects ELF architecture, or you can specify explicitly
    ql = Qiling(
        argv=[binary_path, "arg_test_123", "--verbose"],
        rootfs=rootfs_path,
        ostype=QL_OS.LINUX,
        archtype=QL_ARCH.ARM,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Set up memory limits and execution timeout (in microseconds: 5 seconds)
    timeout_us = 5_000_000
    
    print("[*] Starting emulation...")
    try:
        # Run execution from the entry point until binary termination
        ql.run(timeout=timeout_us)
        print(f"[+] Execution completed successfully with exit code: {ql.os.exit_code}")
    except Exception as err:
        print(f"[-] Execution stopped or timed out: {err}", file=sys.stderr)

if __name__ == "__main__":
    # Example paths (using standard Qiling rootfs layout)
    TARGET_BIN = "rootfs/arm_linux/bin/arm_hello"
    ROOTFS_DIR = "rootfs/arm_linux"
    
    run_cross_arch_sandbox(TARGET_BIN, ROOTFS_DIR)
