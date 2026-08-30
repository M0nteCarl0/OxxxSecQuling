# ⚡️ ✂️ Dynamic Binary Patching & Control Flow Hijacking (Python practice)

When reverse engineering software protected by hardware dongles, license signature verifications, integrity checks, or anti-tamper hashes, modifying the binary on disk invalidates digital signatures and triggers checksum alarms. Qiling allows you to perform in-memory dynamic binary patching (`ql.patch()`) and register-level control flow hijacking during runtime. You can NOP out conditional branch checks, flip CPU condition flags, or rewrite instructions on the fly without touching a single byte on the physical disk.

## 🧠 Core Concept
- **In-Memory Byte Patching (`ql.patch()`)**: Overwrite opcodes in guest memory before execution or upon reaching specific runtime trigger conditions.
- **NOPing Conditional Jumps**: Replace verification branches (`JZ`, `JNZ`, `BEQ`, `BNE`) with NOP sleds to force execution down target code paths.
- **Dynamic Flag Flipping**: Intercept execution right before conditional branches and modify CPU status flags (Zero Flag `ZF`, Carry Flag `CF`).
- **Bypassing Checksum Verifications**: Calculate runtime patches dynamically after internal self-integrity validation loops finish.
- **Zero-Disk Footprint**: Original sample files remain completely pristine and unmodified for forensic integrity.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Defeating software licensing, hardware dongle checks, and serial key validations in crackmes.
- Forcing execution down unexplored or hidden code branches during vulnerability audits.
- Bypassing self-integrity hashing routines by applying patches only after hash verification loops execute.
- Neutralizing emergency kill-switches and anti-tamper triggers in analyzed malware.
- Simulating fault injection attacks (clock glitches, bit flips) by mutating opcodes at specific cycle counts.

## ⚠️ Caveats & Responsible Practice
- **Instruction Length**: When patching with NOPs, ensure the replacement byte length exactly matches the original instruction length (e.g., 2 bytes for short `JZ`, 6 bytes for near `JNZ`).
- **ARM Thumb Mode**: On ARM, Thumb instructions are 2 or 4 bytes (e.g., `NOP` is `0x00 0xbf`), whereas ARM mode NOP is `0x00 0x00 0xa0 0xe1`.
- **Instruction Cache Invalidation**: In some architectures, modifying code pages requires notifying Unicorn's Translation Block cache; applying hooks before execution starts is recommended.
- **Memory Permissions**: Ensure the target code page has write permissions enabled prior to patching.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [x86_64 Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/x8664_linux)
- **License Validator Crackme Sample**: [Qiling Crackme Benchmarks](https://github.com/qilingframework/qiling/tree/master/examples/crackmes)
- **Binary Patching API**: [qiling/core.py (patch)](https://github.com/qilingframework/qiling/blob/master/qiling/core.py)
## 🔗 Resources
- Qiling Patch API Reference (https://docs.qiling.io/en/latest/patch/)
- x86/x64 Opcode Reference (http://ref.x86asm.net/)

#Qiling #BinaryPatching #ReverseEngineering #Crackme #ExploitDev #FaultInjection #CyberSecurity #Python
