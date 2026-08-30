# ⚡️ 🧩 Precision Memory Mapping, Injection, and Struct Layout in Qiling (Python practice)

When reverse engineering standalone functions, proprietary decoders, or unpacking payloads, you rarely want to execute an entire heavy application from `main()`. Instead, you often need to jump directly into an isolated target function. To do this successfully, you must allocate memory regions, configure permissions (Read/Write/Execute), inject test structures, and populate CPU registers. Qiling's `ql.mem` subsystem provides granular control over the virtual address space, bridging Unicorn's raw memory management with OS-aware structure helpers.

## 🧠 Core Concept
- **Custom Virtual Memory Layout**: Allocate and map arbitrary memory pages using `ql.mem.map()` with explicit permission bits (`UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC`).
- **Direct Binary Structure Packing**: Write raw byte payloads, C structs, and endian-aware integers directly into guest virtual addresses with `ql.mem.write()`.
- **Memory Protection Transitions**: Dynamically change page permissions using `ql.mem.protect()` to simulate runtime heap/stack memory hardening.
- **Pattern & Signature Scanning**: Search guest memory for byte signatures, decrypted strings, or shellcode headers using `ql.mem.search()`.
- **Memory Map Introspection**: Inspect the entire guest virtual memory layout, stack base, and mapped libraries using `ql.mem.show_map()`.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Unit-testing stripped C/C++ firmware functions in isolation without executing `main()`.
- Emulating isolated cryptographic hashing algorithms with controlled input structures.
- Injecting simulated OS environment blocks (PEB on Windows, AUXV vectors on Linux).
- Reconstructing heap memory layouts for heap exploitation proof-of-concept validation.
- Searching for decrypted credentials in memory after selective decryption routines finish.

## ⚠️ Caveats & Responsible Practice
- **Page Alignment**: All `ql.mem.map()` calls must use sizes and addresses that are multiples of 0x1000 (4KB page size).
- **Memory Overlaps**: Mapping an address that collides with already loaded ELF/PE segments will raise an unhandled collision exception.
- **Endianness Awareness**: Always use explicit struct packing formats (`<` for Little-Endian, `>` for Big-Endian).
- **Stack Space**: Ensure adequate stack memory is mapped and the stack pointer register (`SP`/`RSP`) is initialized when calling subroutines.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [ARM64 Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/arm64_linux)
- **Sample Target Binary**: `rootfs/arm64_linux/bin/crypto_lib.so` ([ARM64 Libraries](https://github.com/qilingframework/rootfs/tree/master/arm64_linux/lib))
- **Memory Test Suite**: [test_memory.py](https://github.com/qilingframework/qiling/blob/master/tests/test_memory.py)
## 🔗 Resources
- Qiling Memory Management Docs (https://docs.qiling.io/en/latest/memory/)
- Python struct module (https://docs.python.org/3/library/struct.html)

#Qiling #MemoryManagement #ReverseEngineering #BinaryAnalysis #ARM64 #CyberSecurity #AppSec #Python
