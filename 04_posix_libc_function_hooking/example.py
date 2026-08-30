#!/usr/bin/env python3
"""
Post 04: Hooking POSIX / libc Functions with High-Level Python Stubs
Neutralizing ptrace anti-debugging and forcing deterministic pseudo-random generation.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# 1. Python stub for ptrace to bypass anti-debugging
def hook_ptrace(ql: Qiling) -> int:
    request = ql.os.function_arg(0)
    pid = ql.os.function_arg(1)
    print(f"[API HOOK] ptrace(request={request}, pid={pid}) intercepted -> Returning 0 (SUCCESS)")
    # Return 0 so binary thinks no debugger is attached
    return 0

# 2. Python stub for rand() to produce deterministic values
def hook_rand(ql: Qiling) -> int:
    fixed_random_value = 0x41414141
    print(f"[API HOOK] rand() intercepted -> Returning deterministic value: 0x{fixed_random_value:x}")
    return fixed_random_value

# 3. Intercept strcmp to log password/key verification
def hook_strcmp(ql: Qiling) -> int:
    s1_ptr = ql.os.function_arg(0)
    s2_ptr = ql.os.function_arg(1)
    
    s1 = ql.os.utils.read_cstring(s1_ptr)
    s2 = ql.os.utils.read_cstring(s2_ptr)
    print(f"[API HOOK] strcmp(s1='{s1}', s2='{s2}')")
    
    # Return 0 (strings match) to force successful validation
    return 0

def run_with_libc_stubs(binary_path: str, rootfs_path: str) -> None:
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DEFAULT)
    
    # Register API hooks by symbol name
    ql.os.set_api("ptrace", hook_ptrace)
    ql.os.set_api("rand", hook_rand)
    ql.os.set_api("strcmp", hook_strcmp)
    
    print("[*] Launching binary with custom POSIX API stubs...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/protected_crackme"
    ROOTFS = "rootfs/x8664_linux"
    run_with_libc_stubs(TARGET, ROOTFS)
