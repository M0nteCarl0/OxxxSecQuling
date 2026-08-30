#!/usr/bin/env python3
"""
Post 24: Dynamic Binary Patching & Control Flow Hijacking
Dynamically patching authentication/license validation routines during emulation without touching disk files.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Address of license check branch in x86_64 crackme:
# 0x401150: 74 1A  (jz 0x40116c -> jumps to "License Invalid! Exit")
# 0x401152: (continues to "License Validated! Unlocking Features...")
LICENSE_BRANCH_ADDR = 0x401150

def hook_before_license_check(ql: Qiling) -> None:
    pc = ql.arch.regs.arch_pc
    print(f"[*] Reached license verification trigger at PC: 0x{pc:08x}")
    
    # Method 1: Dynamically patch instructions with NOPs (0x90, 0x90) in memory
    print("  [+] Applying in-memory NOP patch to conditional jump...")
    ql.patch(LICENSE_BRANCH_ADDR, b"\x90\x90")
    
    # Method 2: Alternatively, flip CPU Zero Flag (ZF) to force branch outcome
    # ql.arch.regs.eflags &= ~(1 << 6) # Clear Zero Flag (ZF)
    print("  [+] Branch successfully hijacked! Valid code path forced.")

def run_patched_emulation(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Dynamic Patching Sandbox for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DEFAULT)
    
    # Hook exact address of license branch
    ql.hook_address(hook_before_license_check, LICENSE_BRANCH_ADDR)
    
    print("[*] Running binary with dynamic in-memory patch...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/license_validator"
    ROOTFS = "rootfs/x8664_linux"
    run_patched_emulation(TARGET, ROOTFS)
