# ⚡️ 🔍 Fine-Grained Memory Access Tracing: Watchpoints & Taint Tracking (Python practice)

Tracking how sensitive data (such as cryptographic keys, credentials, or untrusted network input) flows through memory is fundamental to both vulnerability research and malware analysis. Hardware debuggers are typically limited to only 4 hardware watchpoint registers, making full-range memory monitoring impossible. Qiling provides software-level memory access hooks (`ql.hook_mem_read()`, `ql.hook_mem_write()`, and `ql.hook_mem_unmapped()`) across unlimited memory ranges without performance penalties from page-fault exceptions.

## 🧠 Core Concept
- **Unlimited Memory Watchpoints**: Monitor reads and writes across arbitrary address ranges with precise byte-level granularity.
- **Data-Flow & Taint Inspection**: Identify every assembly instruction that accesses, reads, or modifies a monitored variable or key buffer.
- **Detecting Memory Corruption**: Intercept out-of-bounds writes, heap overflow corruption, and use-after-free conditions in real time.
- **Unmapped Memory Fault Trapping (`hook_mem_unmapped`)**: Catch wild pointer dereferences and analyze exploit crashes before segmentation faults kill the process.
- **Call-Stack Reconstruction**: Capture register state and return addresses whenever sensitive memory regions are accessed.

## 💻 Implementation Example
```python
#!/usr/bin/env python3
"""
Post 15: Fine-Grained Memory Access Tracing
Attaching memory write hooks to sensitive memory regions and logging every instruction modifying crypto keys.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Address range of the sensitive cryptographic key in memory
KEY_BUFFER_BASE = 0x603000
KEY_BUFFER_SIZE = 32 # 256-bit AES key

def hook_key_write_watchpoint(ql: Qiling, access: int, addr: int, size: int, value: int) -> None:
    pc = ql.arch.regs.arch_pc
    
    # Read the instruction bytes at current PC for disassembly reference
    ins_bytes = ql.mem.read(pc, 4)
    print(f"[WATCHPOINT TRIGGERED] Write Access at 0x{addr:08x} (Size: {size} bytes, Val: 0x{value:x})")
    print(f"  -> Instruction PC: 0x{pc:08x} | Opcode: {ins_bytes.hex()}")
    print(f"  -> Current Stack Pointer (SP): 0x{ql.arch.regs.arch_sp:08x}")
    print(f"  -> General Registers: R0=0x{ql.arch.regs.r0:x}, R1=0x{ql.arch.regs.r1:x}")

def hook_unmapped_access_handler(ql: Qiling, access: int, addr: int, size: int, value: int) -> bool:
    print(f"[!] MEMORY FAULT: Illegal unmapped access at address: 0x{addr:08x} from PC: 0x{ql.arch.regs.arch_pc:08x}")
    # Returning False halts emulation; returning True allows custom mapping recovery
    return False

def run_memory_tracing_sandbox(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Memory Watchpoint Sandbox for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.ARM, verbose=QL_VERBOSE.DISABLED)
    
    # Hook memory writes specifically on our target key address range
    ql.hook_mem_write(hook_key_write_watchpoint, begin=KEY_BUFFER_BASE, end=KEY_BUFFER_BASE + KEY_BUFFER_SIZE)
    
    # Hook unmapped memory faults to catch buffer overflows and crashes
    ql.hook_mem_unmapped(hook_unmapped_access_handler)
    
    print("[*] Running binary with active memory watchpoints...")
    try:
        ql.run()
    except Exception as err:
        print(f"[*] Execution finished: {err}")

if __name__ == "__main__":
    TARGET = "rootfs/arm_linux/bin/crypto_manager"
    ROOTFS = "rootfs/arm_linux"
    run_memory_tracing_sandbox(TARGET, ROOTFS)
```

## 🔥 Use Cases
- Taint analysis: Tracking untrusted network input from `recv()` through internal processing buffers.
- Catching subtle Use-After-Free (UAF) and Out-Of-Bounds (OOB) memory corruption vulnerabilities.
- Identifying which cryptographic subroutines read or modify master encryption keys.
- Auditing proprietary binary license validation routines to pinpoint validation flag addresses.
- Debugging dangling pointers and memory leaks in cross-compiled embedded firmware.

## ⚠️ Caveats & Responsible Practice
- **Callback Performance**: Narrow down the `begin` and `end` address boundaries to minimize hook invocation overhead.
- **Write Values**: In memory write hooks, the `value` argument represents the raw integer value being written to memory.
- **Multi-byte Writes**: A single SIMD or 64-bit store instruction may trigger a write of 8, 16, or 32 bytes.
- **Fault Recovery**: If `hook_mem_unmapped` returns `True`, you must map valid memory at that address via `ql.mem.map()` before returning.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [ARM Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/arm_linux)
- **Sample Crypto Manager**: `rootfs/arm_linux/bin/crypto_manager` ([ARM Binaries](https://github.com/qilingframework/qiling/tree/master/examples/rootfs/arm_linux/bin))
- **Memory Hooks Reference**: [qiling/core.py (hook_mem_read, hook_mem_write)](https://github.com/qilingframework/qiling/blob/master/qiling/core.py)
## 🔗 Resources
- Qiling Memory Hook API (https://docs.qiling.io/en/latest/hook/#memory-hooks)
- Unicorn Engine Hook Documentation (https://www.unicorn-engine.org/docs/)

#Qiling #MemoryWatchpoint #TaintAnalysis #ReverseEngineering #VulnerabilityResearch #ExploitDev #CyberSecurity #Python
