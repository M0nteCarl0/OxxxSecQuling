#!/usr/bin/env python3
"""
Post 25: Direct Function Calling & Symbol Execution
Loading a proprietary crypto shared library and executing an internal hashing function directly with custom buffers.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import struct

def run_direct_function_invocation(lib_path: str, rootfs_path: str) -> None:
    print(f"[*] Loading shared library: {lib_path}...")
    ql = Qiling(
        argv=[lib_path],
        rootfs=rootfs_path,
        ostype=QL_OS.LINUX,
        archtype=QL_ARCH.X8664,
        verbose=QL_VERBOSE.DISABLED
    )
    
    # 1. Resolve exported symbol address for: uint32_t calculate_token_hash(char *input, int len, uint32_t seed)
    symbol_name = "calculate_token_hash"
    func_addr = ql.loader.import_symbols.get(symbol_name)
    
    if not func_addr:
        # Fallback to known static function offset if stripped
        func_addr = 0x4014F0
    print(f"[+] Located target function '{symbol_name}' at: 0x{func_addr:08x}")
    
    # 2. Allocate guest memory for test input buffer
    test_input = b"UserAdminSessionToken_2026"
    buf_addr = ql.os.heap.alloc(len(test_input) + 1)
    ql.mem.write(buf_addr, test_input + b"\x00")
    
    seed = 0x1337CAFE
    
    # 3. Call target function directly using Qiling's OS function caller
    print(f"[*] Calling {symbol_name}(buf=0x{buf_addr:08x}, len={len(test_input)}, seed=0x{seed:x})...")
    return_value = ql.os.function_call(func_addr, [buf_addr, len(test_input), seed])
    
    print("=" * 60)
    print(f"[+] Function execution returned: 0x{return_value:08x} ({return_value})")
    print("=" * 60)

if __name__ == "__main__":
    TARGET_LIB = "rootfs/x8664_linux/lib/libtoken_crypto.so"
    ROOTFS = "rootfs/x8664_linux"
    run_direct_function_invocation(TARGET_LIB, ROOTFS)
