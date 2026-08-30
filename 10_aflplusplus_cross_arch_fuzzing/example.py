#!/usr/bin/env python3
"""
Post 10: Integrating Qiling with AFL++ Forkserver for Cross-Arch Fuzzing
Writing an AFL++ persistent fuzzing harness in Python for an ARM ELF network parser using `ql.fuzz()`.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import sys

# Callback invoked by AFL++ forkserver on every mutated testcase input
def afl_place_input(ql: Qiling, input_bytes: bytes, user_data: dict) -> bool:
    buffer_addr = user_data["buf_addr"]
    max_len = user_data["max_len"]
    
    # Truncate input if it exceeds buffer capacity
    data = input_bytes[:max_len]
    
    # Write fuzzer-generated testcase directly into target memory
    ql.mem.write(buffer_addr, data)
    
    # Update function argument registers (r0 = buffer_ptr, r1 = data_length)
    ql.arch.regs.r0 = buffer_addr
    ql.arch.regs.r1 = len(data)
    
    # Return True to proceed with execution, False to discard
    return True

# Validation callback executed upon crash detection
def afl_validate_crash(ql: Qiling, result: bool, user_data: dict) -> bool:
    # Return True to report this crash to AFL++
    print(f"[!] Crash identified at PC: 0x{ql.arch.regs.arch_pc:08x}")
    return True

def start_afl_fuzzing(binary_path: str, rootfs_path: str) -> None:
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.ARM, verbose=QL_VERBOSE.DISABLED)
    
    # Target function boundaries
    ENTRY_POINT = 0x10540 # parser_entry()
    EXIT_POINT = 0x10620  # parser_return
    INPUT_BUF = 0x7FFF1000
    
    user_context = {"buf_addr": INPUT_BUF, "max_len": 512}
    
    print("[*] Starting AFL++ Persistent Fuzzing Harness...")
    # ql.fuzz() interfaces with AFL++ forkserver (e.g. `afl-fuzz -U -i in -o out -- python3 harness.py`)
    try:
        ql.fuzz(
            input_file=sys.argv[1] if len(sys.argv) > 1 else None,
            place_input_callback=afl_place_input,
            validate_crash_callback=afl_validate_crash,
            always_validate=False,
            user_data=user_context,
            begin=ENTRY_POINT,
            end=EXIT_POINT
        )
    except Exception as err:
        print(f"[-] Fuzzing session terminated: {err}")

if __name__ == "__main__":
    TARGET = "rootfs/arm_linux/bin/vuln_iot_parser"
    ROOTFS = "rootfs/arm_linux"
    start_afl_fuzzing(TARGET, ROOTFS)
