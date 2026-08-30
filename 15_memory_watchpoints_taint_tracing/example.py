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
