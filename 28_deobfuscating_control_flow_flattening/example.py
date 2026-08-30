#!/usr/bin/env python3
"""
Post 28: Deobfuscating Control-Flow Flattening via Instruction Tracing
Tracing state variable mutations in flattened code blocks and extracting genuine basic block execution order.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Address boundaries of the flattened function
FUNC_BASE = 0x401000
FUNC_END  = 0x401600
DISPATCHER_BLOCK_ADDR = 0x401050

execution_trace = []
state_history = []

def trace_flattened_blocks(ql: Qiling, address: int, size: int) -> None:
    # Filter trace to target function address space
    if FUNC_BASE <= address < FUNC_END:
        # Check if execution reached the central dispatcher block
        if address == DISPATCHER_BLOCK_ADDR:
            # Read the current state variable value (stored in EAX/RAX)
            state_val = ql.arch.regs.rax
            state_history.append((hex(address), hex(state_val)))
            print(f"[DISPATCHER HIT] Central Dispatcher 0x{address:08x} -> Next State Variable: 0x{state_val:x}")
        else:
            execution_trace.append(address)

def run_deobfuscator_trace(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Control-Flow Deobfuscator Sandbox for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DISABLED)
    
    # Hook basic block entries
    ql.hook_block(trace_flattened_blocks)
    
    print("[*] Running obfuscated function to capture true execution path...")
    try:
        ql.run(begin=FUNC_BASE, end=FUNC_END)
    except Exception:
        pass
        
    print("=" * 60)
    print(f"[+] Trace Complete: Captured {len(execution_trace)} basic blocks and {len(state_history)} state transitions.")
    print("[+] Recovered True Execution Order:")
    for idx, (disp, state) in enumerate(state_history[:10]):
        print(f"    Step {idx + 1:02d}: State Var = {state}")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/ollvm_flattened_app"
    ROOTFS = "rootfs/x8664_linux"
    run_deobfuscator_trace(TARGET, ROOTFS)
