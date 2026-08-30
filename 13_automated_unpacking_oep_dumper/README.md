# ⚡️ 📦 Automated Unpacking & OEP Memory Dumper with Qiling (Python practice)

Packers, crypters, and protectors (such as UPX, custom XOR loaders, or commercial packers) conceal the original code by decrypting executable sections into newly allocated memory at runtime before transferring control to the Original Entry Point (OEP) via a tail jump. Static unpackers break whenever packers undergo minor revisions. Qiling allows you to build generic, dynamic unpackers by placing instruction hooks that monitor program counter transitions between memory regions and dumping fully unpacked PE/ELF memory images automatically upon reaching the OEP.

## 🧠 Core Concept
- **Dynamic Tail Jump Detection**: Monitor execution transitions from unpacker stub memory addresses into the newly decrypted payload address range.
- **Instruction-Level Code Hooking (`ql.hook_code()`)**: Inspect every executed assembly instruction, current program counter (`PC`), and target branch addresses.
- **Automated OEP Identification**: Detect when the execution leaves unpacker stub memory blocks and enters the main code section (`.text`).
- **Live Process Image Dumping**: Read and reconstruct decrypted memory sections using `ql.mem.read()` directly into a clean executable file on disk.
- **Zero Anti-Unpacking Evasion**: Bypass anti-dumping tricks, timing checks, and debugger detections with Qiling's isolated emulation.

## 💻 Implementation Example
```python
#!/usr/bin/env python3
"""
Post 13: Automated Unpacking & OEP Memory Dumper
Emulating a packed binary, detecting the tail jump to unpacked code section, and dumping memory at OEP.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Known boundaries of unpacker stub vs target code section
UNPACKER_STUB_BASE = 0x408000
UNPACKER_STUB_END  = 0x40A000
TARGET_CODE_BASE   = 0x401000
TARGET_CODE_END    = 0x406000

dumped = False

def detect_oep_and_dump(ql: Qiling, address: int, size: int) -> None:
    global dumped
    
    # Check if execution has transitioned from unpacker stub into main code section
    if not dumped and TARGET_CODE_BASE <= address < TARGET_CODE_END:
        print("=" * 60)
        print(f"[!] OEP REACHED at address: 0x{address:08x}!")
        print(f"    Instruction size: {size} bytes")
        
        # Read the newly decrypted .text section from memory
        unpacked_code_size = TARGET_CODE_END - TARGET_CODE_BASE
        unpacked_bytes = ql.mem.read(TARGET_CODE_BASE, unpacked_code_size)
        
        # Dump the clean unpacked section to disk
        output_file = "unpacked_text_section.bin"
        with open(output_file, "wb") as f:
            f.write(unpacked_bytes)
            
        print(f"[+] Successfully dumped {len(unpacked_bytes)} bytes of unpacked code to '{output_file}'")
        print("=" * 60)
        
        dumped = True
        # Stop emulation now that unpacking is complete
        ql.stop()

def run_unpacking_engine(packed_binary: str, rootfs_path: str) -> None:
    print(f"[*] Loading packed binary: {packed_binary}...")
    ql = Qiling([packed_binary], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DISABLED)
    
    # Hook every instruction execution
    ql.hook_code(detect_oep_and_dump)
    
    print("[*] Emulating unpacker routine...")
    try:
        ql.run()
    except Exception as err:
        print(f"[*] Emulation completed: {err}")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/packed_sample_elf"
    ROOTFS = "rootfs/x8664_linux"
    run_unpacking_engine(TARGET, ROOTFS)
```

## 🔥 Use Cases
- Unpacking unknown malware droppers and ransomware stubs automatically in triage pipelines.
- Defeating custom XOR/RC4/AES loaders without manually reversing decoding loops in IDA.
- Extracting clean, decompilable ELF/PE binaries for Ghidra or Binary Ninja static analysis.
- Detecting multi-stage loaders that decrypt subsequent layers into dynamic heap memory.
- Generating clean signatures (YARA rules, hashes) from the genuine unpacked payload core.

## ⚠️ Caveats & Responsible Practice
- **Performance with Instruction Hooks**: `hook_code()` adds execution overhead; filter the hook address range if the unpacker stub boundaries are known.
- **IAT Reconstruction**: Dynamic memory dumps contain resolved API pointers; for complete standalone execution, IAT / relocation fixup may be required (e.g., using `pefile` or `Scylla`).
- **Self-Modifying Pages**: Ensure memory protection flags (`PROT_WRITE | PROT_EXEC`) allow in-place modification during unpacking.
- **Multi-Layer Packers**: For multi-stage crypters, maintain a state counter to dump each subsequent layer upon transition.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [x86_64 Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/x8664_linux)
- **Packed Sample Binaries**: [Qiling Unpacking Examples](https://github.com/qilingframework/qiling/tree/master/examples/unpacking)
- **UPX Reference Repository**: [UPX Ultimate Packer for eXecutables](https://github.com/upx/upx)
## 🔗 Resources
- Qiling Hooking API (https://docs.qiling.io/en/latest/hook/)
- Unpacking Concepts Guide (https://resources.infosecinstitute.com/topic/unpacking-binaries/)

#Qiling #Unpacking #ReverseEngineering #MalwareAnalysis #OEP #BinaryAnalysis #CyberSecurity #AppSec
