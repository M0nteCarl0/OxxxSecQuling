#!/usr/bin/env python3
"""
Post 02: Kernel Syscall Interception and Redirection
Intercepting `sys_openat` and `sys_read` on MIPS Linux to monitor file access and alter return buffers.
"""

from qiling import Qiling
from qiling.const import QL_INTERCEPT, QL_VERBOSE, QL_ARCH, QL_OS
import os

def hook_sys_openat(ql: Qiling, dfd: int, filename_ptr: int, flags: int, mode: int) -> None:
    # Read the null-terminated string from the guest memory pointer
    filepath = ql.os.utils.read_cstring(filename_ptr)
    print(f"[SYSCALL] sys_openat(dfd={dfd}, path='{filepath}', flags=0x{flags:x})")
    
    # If the binary attempts to read sensitive configuration, redirect to a decoy file
    if "/etc/shadow" in filepath or "/etc/config/admin.conf" in filepath:
        print(f"  [!] Intercepted access to sensitive file: {filepath} -> Redirecting to decoy!")
        decoy_path = "/tmp/decoy_config.conf"
        # Write decoy path into memory and update pointer
        ql.mem.write(filename_ptr, decoy_path.encode() + b"\x00")

def hook_sys_read_exit(ql: Qiling, fd: int, buf_ptr: int, count: int) -> None:
    # Read the returned buffer after the kernel finishes sys_read
    ret_val = ql.arch.regs.arch_pc # or architecture return register
    print(f"[SYSCALL EXIT] sys_read(fd={fd}, count={count})")

def setup_syscall_monitoring(binary_path: str, rootfs_path: str) -> None:
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.MIPS, verbose=QL_VERBOSE.DEFAULT)
    
    # Intercept sys_openat at entry
    ql.os.set_syscall("sys_openat", hook_sys_openat, stage=QL_INTERCEPT.CALL)
    # Intercept sys_read at exit stage
    ql.os.set_syscall("sys_read", hook_sys_read_exit, stage=QL_INTERCEPT.EXIT)
    
    print("[*] Running binary with active syscall hooks...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/mips32el_linux/bin/mips_iot_daemon"
    ROOTFS = "rootfs/mips32el_linux"
    setup_syscall_monitoring(TARGET, ROOTFS)
