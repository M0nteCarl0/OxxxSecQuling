# ⚡️ 🐚 Raw Shellcode Emulation & Staged Shellcode Decoding with Qiling (Python practice)

When analyzing exploitation payloads, malicious macro drops, or memory dumps, security analysts frequently encounter position-independent raw shellcode without PE/ELF metadata, headers, or entrypoint tables. Emulating raw shellcode in standalone Unicorn requires manually allocating memory, initializing stack pointers, mapping segment registers, and building fake kernel structures. Qiling's raw code emulation mode provides instant, zero-boilerplate shellcode execution with full access to OS API interception, memory hooks, and instruction-level tracing.

## 🧠 Core Concept
- **Headerless Execution (`code=...`)**: Direct execution of raw binary bytecode without requiring PE/ELF headers or disk file structures.
- **Automatic Stack & Register Setup**: Automatically initializes the stack pointer (`ESP`/`RSP`/`SP`), base pointer, and execution segment registers.
- **Self-Modifying Code Tracing**: Intercept memory write operations (`ql.hook_mem_write()`) to capture dynamically decrypted stage-2 payloads as they unpack in memory.
- **Cross-Architecture Shellcode Analysis**: Analyze x86, x86_64, ARM, or MIPS shellcode payloads using identical Python inspection routines.
- **API Call Resolution**: Even raw shellcode that resolves APIs dynamically via PEB traversal or hash parsing can invoke Qiling's simulated Win32/POSIX API stubs.

## 💻 Implementation Example
```python
#!/usr/bin/env python3
"""
Post 07: Raw Shellcode Emulation & Staged Shellcode Decoding
Emulating polymorphic x86_64 shellcode, hooking instruction writes to monitor dynamic self-decryption.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Example polymorphic x86_64 shellcode (XOR-decoder stub + encrypted payload)
# Stub: XORs 16 bytes starting at target offset with key 0x5A
SHELLCODE_BYTES = (
    b"\x48\x31\xc0"                          # xor rax, rax
    b"\x48\x8d\x3d\x0a\x00\x00\x00"      # lea rdi, [rip + 10] -> payload
    b"\xb9\x10\x00\x00\x00"              # mov ecx, 16
    # loop_start:
    b"\x80\x37\x5a"                          # xor byte ptr [rdi], 0x5a
    b"\x48\xff\xc7"                          # inc rdi
    b"\xe2\xf8"                              # loop loop_start
    b"\x90\x90\x90\x90"                      # NOP sled
    # Encrypted payload bytes (XORed with 0x5A)
    b"\x12\x34\x56\x78\x9A\xBC\xDE\xF0\x0F\x1E\x2D\x3C\x4B\x5A\x69\x78"
)

def hook_memory_modification(ql: Qiling, access: int, addr: int, size: int, value: int) -> None:
    # Read the updated byte from memory after modification
    written_data = ql.mem.read(addr, size)
    pc = ql.arch.regs.arch_pc
    print(f"[DECODER EVENT] PC=0x{pc:08x} -> Wrote {size} byte(s) at 0x{addr:08x}: {written_data.hex()} (ASCII: {written_data})")

def run_shellcode_sandbox(code_bytes: bytes) -> None:
    print(f"[*] Initializing Qiling for raw x86_64 shellcode ({len(code_bytes)} bytes)...")
    
    # Initialize Qiling with raw bytecode
    ql = Qiling(
        code=code_bytes,
        archtype=QL_ARCH.X8664,
        ostype=QL_OS.LINUX,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Hook memory writes to capture decoded stage-2 payload in real time
    ql.hook_mem_write(hook_memory_modification)
    
    print("[*] Running shellcode emulation...")
    try:
        ql.run()
    except Exception as err:
        print(f"[!] Emulation reached boundary or halt: {err}")

if __name__ == "__main__":
    run_shellcode_sandbox(SHELLCODE_BYTES)
```

## 🔥 Use Cases
- Analyzing staged shellcode and egg-hunters extracted from network exploit captures.
- Automatically dumping unpacked payload buffers from self-decrypting malicious macros.
- Validating security detection signatures (YARA rules, EDR heuristics) against emulated shellcode.
- Simulating custom embedded shellcode for ARM/MIPS IoT exploitation research.
- Extracting hardcoded C2 IP addresses and ports embedded in position-independent shellcode.

## ⚠️ Caveats & Responsible Practice
- **API Resolution Hooks**: Windows shellcode traversing the PEB (`fs:[0x30]` or `gs:[0x60]`) requires `ostype=QL_OS.WINDOWS` so Qiling populates the virtual PEB.
- **Stack Size**: Raw code execution maps a default stack region; expand the stack if the shellcode allocates large local stack buffers.
- **Termination Condition**: Raw shellcode lacks standard `exit()` calls; set a specific `end` address or catch execution faults upon completion.
- **Memory Permissions**: Ensure the memory region containing the shellcode has `EXEC` permissions.

## 📦 Test Data & Sample Binaries
- **Test Payload**: Included directly in `example.py` (Self-contained position-independent x86_64 decoder bytecode)
- **Shellcode Reference Archive**: [Shell-Storm x86_64 Shellcode Database](http://shell-storm.org/shellcode/)
- **Qiling Shellcode Tests**: [test_shellcode.py](https://github.com/qilingframework/qiling/blob/master/tests/test_shellcode.py)
## 🔗 Resources
- Qiling Shellcode Emulation Guide (https://docs.qiling.io/en/latest/shellcode/)
- Shell-Storm Database (http://shell-storm.org/shellcode/)

#Qiling #Shellcode #ReverseEngineering #MalwareAnalysis #ExploitDev #SecurityResearch #BinaryAnalysis #Python
