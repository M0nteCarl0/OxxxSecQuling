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
