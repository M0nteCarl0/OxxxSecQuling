# ⚡️ 🔀 Kernel Syscall Interception and Redirection with Qiling (Python practice)

In binary analysis, monitoring and modifying system calls is the gold standard for understanding how software interacts with the operating system kernel. When analyzing obfuscated binaries or malware, native kernel debugging requires complex ring-0 hooks or kernel drivers. Qiling abstracts the entire system call layer: every `sys_enter` and `sys_exit` passes through a modular dispatcher in user-space Python, allowing researchers to intercept, log, rewrite parameters, and spoof return values transparently before the binary ever notices.

## 🧠 Core Concept
- **User-Space Syscall Dispatcher**: Intercepts architecture-specific syscall instructions (`svc`, `syscall`, `sysenter`, `int 0x80`) cleanly in user space.
- **Bi-Directional Interception**: Hook syscalls at `QL_INTERCEPT.CALL` (to inspect/modify input arguments) or `QL_INTERCEPT.EXIT` (to spoof return values).
- **Path & Argument Spoofing**: Intercept file system calls (`sys_open`, `sys_openat`) to redirect access to virtual or isolated decoy files.
- **Cross-Architecture Argument Resolution**: Qiling automatically maps platform-specific calling conventions (e.g., registers `r0`-`r3` on ARM, `rdi`/`rsi`/`rdx` on x86_64, `a0`-`a3` on MIPS).
- **Kernel Error Simulation**: Force syscalls to return arbitrary POSIX error codes (e.g., `-EACCES`, `-ENOENT`) to evaluate error-handling branch coverage.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Detecting malware persistence attempts (monitoring `sys_unlink`, `sys_rename`, `sys_symlink`).
- Spoofing hardware identification syscalls (`sys_uname`, `sys_sysinfo`) to bypass anti-VM checks.
- Redirecting hardcoded system files to virtual analysis sandboxes.
- Fuzzing error-handling logic by selectively injecting failed syscall return codes.
- Auditing proprietary cryptographic daemon communication via intercepted IPC syscalls.

## ⚠️ Caveats & Responsible Practice
- **Syscall Numbers Vary Across Architectures**: Use syscall string names (`'sys_openat'`) rather than raw integers for portable scripts.
- **Memory Pointer Modification**: When rewriting string arguments in memory, ensure the new string fits within allocated memory or write to a dedicated scratch buffer.
- **Stage Selection**: Use `QL_INTERCEPT.CALL` to manipulate input arguments and `QL_INTERCEPT.EXIT` to inspect/overwrite return values.
- **Calling Convention Safety**: Do not manually modify scratch registers during syscall callbacks unless intentionally altering program state.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [MIPS32 Little-Endian RootFS](https://github.com/qilingframework/rootfs/tree/master/mips32el_linux)
- **Sample Target Binary**: `rootfs/mips32el_linux/bin/mips_iot_daemon` ([MIPS Test Binaries](https://github.com/qilingframework/qiling/tree/master/examples/rootfs/mips32el_linux/bin))
- **Syscall Testing Suite**: [Linux Syscall Test Suite](https://github.com/qilingframework/qiling/tree/master/tests/test_posix.py)
## 🔗 Resources
- Qiling Syscall Documentation (https://docs.qiling.io/en/latest/syscall/)
- Linux Syscall Tables (https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md)

#Qiling #Syscalls #BinaryAnalysis #ReverseEngineering #MIPS #KernelEmulation #SecurityResearch #Python
