# ⚡️ 🎯 Direct Function Calling & Symbol Execution with Qiling (Python practice)

When auditing shared libraries (`.so` on Linux, `.dll` on Windows, `.dylib` on macOS), analysts often need to test a specific exported hashing algorithm, signature verifier, or token generator with thousands of custom inputs without writing a C harness or compiling wrapper binaries. Qiling features high-level function invocation (`ql.os.function_call()`). It automatically resolves dynamic symbol names, allocates stack frames, sets up register-based calling conventions, executes the target function in isolation, and returns the result directly to Python.

## 🧠 Core Concept
- **Dynamic Symbol Resolution**: Locate exported function addresses automatically from ELF/PE symbol tables (`ql.loader.import_symbols`).
- **Native Python Argument Passing (`ql.os.function_call()`)**: Pass Python integers, strings, and byte arrays directly into binary functions without manual register manipulation.
- **Automatic ABI Management**: Qiling sets up the appropriate architecture calling convention (System V AMD64, Microsoft x64, ARM AAPCS) transparently.
- **Direct Output Extraction**: Capture return values directly in Python as native return types or inspect modified memory pointers.
- **Zero Compilation Wrapper Overhead**: Call complex C/C++ library routines directly without compiling C test harnesses or fighting cross-toolchains.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Fuzzing individual parsing and cryptographic functions in proprietary shared libraries.
- Generating authentication tokens and session signatures using genuine vendor algorithms.
- Differential testing of hashing algorithms against reference standard implementations.
- Unit testing proprietary reverse engineered firmware libraries during vulnerability research.
- Automating CTF challenge solving for shared library cracking challenges.

## ⚠️ Caveats & Responsible Practice
- **Heap Allocation**: Strings or structs passed by reference must reside in valid mapped memory allocated via `ql.os.heap.alloc()` or `ql.mem.map()`.
- **Library Initialization**: If the target library requires `_init()` or `.init_array` constructors to run first, initialize the loader before calling subroutines.
- **Return Value Types**: Return values are retrieved from the architecture return register (e.g. `RAX` on x64, `R0` on ARM); cast appropriately in Python.
- **Floating-Point Arguments**: Functions taking floating-point arguments (via XMM/NEON registers) require manual vector register setup.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [x86_64 Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/x8664_linux)
- **Target Shared Libraries (.so)**: [x86_64 Shared Libraries Archive](https://github.com/qilingframework/rootfs/tree/master/x8664_linux/lib)
- **Function Call Engine**: [qiling/os/posix/function.py](https://github.com/qilingframework/qiling/blob/master/qiling/os/posix/function.py)
## 🔗 Resources
- Qiling Function Call Documentation (https://docs.qiling.io/en/latest/function_call/)
- System V AMD64 Calling Convention (https://wiki.osdev.org/System_V_ABI)

#Qiling #FunctionCalling #SharedLibraries #ReverseEngineering #CryptoAnalysis #BinaryAnalysis #CyberSecurity #Python
