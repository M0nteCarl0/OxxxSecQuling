#!/usr/bin/env python3
"""
Post 18: Bypassing Anti-Analysis, Anti-VM & Timing Checks
Creating a comprehensive anti-anti-analysis hook suite in Qiling that transparently neutralizes evasion tactics.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Monotonic cycle counter to defeat RDTSC timing checks
fake_cycle_counter = 1000

def hook_rdtsc(ql: Qiling) -> None:
    global fake_cycle_counter
    fake_cycle_counter += 150 # Increment by a small, realistic instruction delta
    
    # RDTSC returns low 32-bits in EAX, high 32-bits in EDX
    eax_val = fake_cycle_counter & 0xFFFFFFFF
    edx_val = (fake_cycle_counter >> 32) & 0xFFFFFFFF
    
    ql.arch.regs.rax = eax_val
    ql.arch.regs.rdx = edx_val
    print(f"[ANTI-ANALYSIS BYPASS] Spoofed RDTSC cycle count: {fake_cycle_counter}")

def hook_is_debugger_present(ql: Qiling) -> int:
    print("[ANTI-ANALYSIS BYPASS] IsDebuggerPresent() intercepted -> Returning 0 (FALSE)")
    return 0

def hook_check_remote_debugger(ql: Qiling) -> int:
    hProcess = ql.os.function_arg(0)
    pbDebuggerPresent_ptr = ql.os.function_arg(1)
    
    print("[ANTI-ANALYSIS BYPASS] CheckRemoteDebuggerPresent() intercepted -> Setting FALSE")
    # Write 0 (FALSE) to the output pointer
    ql.mem.write(pbDebuggerPresent_ptr, b"\x00\x00\x00\x00")
    return 1 # Returns non-zero for API success

def setup_stealth_sandbox(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Stealth Sandbox for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.WINDOWS, archtype=QL_ARCH.X86, verbose=QL_VERBOSE.DEFAULT)
    
    # 1. Hook Win32 Anti-Debug APIs
    ql.os.set_api("IsDebuggerPresent", hook_is_debugger_present)
    ql.os.set_api("CheckRemoteDebuggerPresent", hook_check_remote_debugger)
    
    # 2. Hook RDTSC instruction
    ql.hook_insn(hook_rdtsc, "rdtsc")
    
    print("[*] Running evasive malware with full anti-analysis countermeasures active...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/x86_windows/bin/evasive_malware.exe"
    ROOTFS = "rootfs/x86_windows"
    setup_stealth_sandbox(TARGET, ROOTFS)
