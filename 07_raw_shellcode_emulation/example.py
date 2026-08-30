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
