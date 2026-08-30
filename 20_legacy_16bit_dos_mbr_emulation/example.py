#!/usr/bin/env python3
"""
Post 20: Legacy 16-bit DOS COM & Real-Mode MBR Emulation
Emulating a 16-bit DOS `.com` crackme, hooking `int 21h` handlers to inspect string I/O and display output.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

def hook_dos_int21(ql: Qiling) -> None:
    # Read AH register (service function number)
    ah = (ql.arch.regs.eax >> 8) & 0xFF
    al = ql.arch.regs.eax & 0xFF
    
    # AH = 0x09: Display $-terminated string at DS:DX
    if ah == 0x09:
        ds = ql.arch.regs.ds
        dx = ql.arch.regs.edx & 0xFFFF
        # Real-mode linear address calculation: Segment * 16 + Offset
        linear_addr = (ds * 16) + dx
        
        # Read string terminated by '$' (DOS convention)
        raw_bytes = ql.mem.read(linear_addr, 128)
        text = raw_bytes.split(b"$")[0].decode("ascii", errors="ignore")
        print(f"[DOS INT 21h | AH=09h Print] '{text}'")
        
    # AH = 0x4C: Terminate Process with Exit Code in AL
    elif ah == 0x4C:
        print(f"[DOS INT 21h | AH=4Ch Exit] Binary terminated with exit code: {al}")
        ql.stop()

def run_dos_sandbox(com_file_path: str) -> None:
    print(f"[*] Initializing 16-bit DOS Real-Mode Sandbox for {com_file_path}...")
    ql = Qiling(
        argv=[com_file_path],
        rootfs="", # No Linux rootfs required for DOS COM files
        ostype=QL_OS.DOS,
        archtype=QL_ARCH.X86,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Hook software interrupt INT 0x21
    ql.hook_intno(hook_dos_int21, 0x21)
    
    print("[*] Starting 16-bit DOS emulation...")
    try:
        ql.run()
    except Exception as err:
        print(f"[*] Emulation ended: {err}")

if __name__ == "__main__":
    TARGET_COM = "rootfs/dos/bin/crackme16.com"
    run_dos_sandbox(TARGET_COM)
