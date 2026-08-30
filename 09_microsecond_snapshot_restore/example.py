#!/usr/bin/env python3
"""
Post 09: Microsecond Snapshot & Restore for High-Speed Fuzzing
Snapshotting an emulated binary right before a parser function and testing 500 mutated payloads.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import random
import time

def setup_snapshot_fuzzer(binary_path: str, rootfs_path: str) -> None:
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DISABLED)
    
    # Target address of the parser function: 0x4012A0, Exit address: 0x401350
    PARSER_ENTRY = 0x4012A0
    PARSER_EXIT = 0x401350
    BUFFER_ADDR = 0x7FFF0000 # Memory buffer where input packet is loaded
    
    # 1. Run binary up to the parser entry point
    print(f"[*] Running binary to initialization target (0x{PARSER_ENTRY:x})...")
    ql.run(end=PARSER_ENTRY)
    
    # 2. Take complete in-memory snapshot of CPU registers, memory map, and OS state
    print("[+] Taking snapshot of process state...")
    saved_snapshot = ql.save()
    
    # 3. Iterative high-speed testing loop
    NUM_ITERATIONS = 500
    print(f"[*] Starting fast fuzzing loop ({NUM_ITERATIONS} iterations)...")
    start_time = time.time()
    
    for i in range(NUM_ITERATIONS):
        # Restore clean state
        ql.restore(saved_snapshot)
        
        # Mutate test payload (32 bytes)
        mutated_payload = bytearray(random.getrandbits(8) for _ in range(32))
        
        # Write mutated test case directly into memory
        ql.mem.write(BUFFER_ADDR, bytes(mutated_payload))
        
        # Set argument registers for the parser (RDI = buffer_ptr, RSI = length)
        ql.arch.regs.rdi = BUFFER_ADDR
        ql.arch.regs.rsi = len(mutated_payload)
        
        try:
            # Execute only the parser function from entry to exit
            ql.run(begin=PARSER_ENTRY, end=PARSER_EXIT)
        except Exception as crash_err:
            print(f"[!] CRASH DETECTED at iteration {i}: {crash_err}")
            print(f"    Payload: {mutated_payload.hex()}")
            break
            
    elapsed = time.time() - start_time
    print(f"[+] Completed {NUM_ITERATIONS} iterations in {elapsed:.3f}s ({NUM_ITERATIONS / elapsed:.1f} exec/s)")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/network_parser"
    ROOTFS = "rootfs/x8664_linux"
    setup_snapshot_fuzzer(TARGET, ROOTFS)
