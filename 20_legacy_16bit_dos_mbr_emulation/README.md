# ⚡️ 💾 Legacy 16-bit DOS COM & Real-Mode MBR Emulation with Qiling (Python practice)

Retro-reversing, legacy industrial control software, master boot record (MBR) bootkits, and classic DOS crackmes operate in 16-bit Real Mode with segmented memory addressing (`CS:IP`, `DS:DX`) and BIOS/DOS software interrupts (`INT 21h`, `INT 10h`, `INT 13h`). Modern x64 operating systems have completely dropped 16-bit execution support (NTVDM). Qiling features a built-in 16-bit DOS / MBR emulation engine (`QL_OSTYPE.DOS`), allowing security researchers to execute and hook 16-bit `.COM` binaries and raw boot sectors with full Python control.

## 🧠 Core Concept
- **16-bit Real-Mode Architecture**: Emulates x86 real-mode segment:offset memory calculation (`Address = Segment * 16 + Offset`).
- **DOS Interrupt Interception (`INT 21h`)**: Intercept standard DOS API services (AH=09h display string, AH=0Ah buffered input, AH=3Dh file open).
- **BIOS Disk & Video Services**: Emulate `INT 10h` video routines and `INT 13h` raw sector read/write operations for MBR analysis.
- **Zero Virtual Machine Setup**: Run legacy 16-bit MS-DOS binaries directly inside a lightweight Python script without DOSBox or FreeDOS VM overhead.
- **Direct Register & Memory Inspection**: Read 16-bit registers (`AX`, `BX`, `CX`, `DX`, `SI`, `DI`, `SP`, `BP`) and memory segments easily.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Analyzing legacy 16-bit ransomware and wiper bootkits targeting Master Boot Records (MBRs).
- Solving retro-computing and 16-bit DOS reverse engineering CTF challenges.
- Auditing legacy SCADA and industrial automation utilities compiled for MS-DOS environments.
- Extracting hardcoded algorithms from historical software preservation archives.
- Teaching real-mode x86 assembly and segment:offset memory models in academic courses.

## ⚠️ Caveats & Responsible Practice
- **Linear vs Segmented Address**: Always convert `Segment:Offset` into a 20-bit linear physical address (`(Segment << 4) + Offset`) when reading guest memory.
- **DOS Interrupt Conventions**: Strings printed via `INT 21h, AH=09h` are terminated by the `$` character, not null bytes.
- **COM File Base**: DOS `.COM` files are loaded at offset `0x0100` within their code segment with the Program Segment Prefix (PSP) occupying `0x0000 - 0x00FF`.
- **Stack Layout**: 16-bit SP operations wrap around the 64KB segment boundary; ensure stack offsets do not overflow.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [16-bit DOS Environment RootFS](https://github.com/qilingframework/rootfs/tree/master/dos)
- **Sample DOS COM Binaries**: [DOS Crackme & 16-bit Samples](https://github.com/qilingframework/qiling/tree/master/examples/dos)
- **DOS Interrupt Dispatcher**: [qiling/os/dos/dos.py](https://github.com/qilingframework/qiling/blob/master/qiling/os/dos/dos.py)
## 🔗 Resources
- Qiling DOS Subsystem (https://docs.qiling.io/en/latest/dos/)
- Ralf Brown's Interrupt List (http://www.ctyme.com/rbrown.htm)

#Qiling #DOS #16Bit #RealMode #ReverseEngineering #RetroComputing #MBR #CyberSecurity
