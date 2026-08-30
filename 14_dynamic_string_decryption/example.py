#!/usr/bin/env python3
"""
Post 14: Dynamic String Decryption & Malware Config Extraction
Emulating an internal string decryption routine at address 0x401820 and extracting all decrypted strings.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Known encrypted string offsets in binary and their lengths
ENCRYPTED_STRING_RECORDS = [
    {"offset": 0x406020, "length": 24, "id": "C2_Primary"},
    {"offset": 0x406040, "length": 18, "id": "C2_Backup"},
    {"offset": 0x406060, "length": 32, "id": "AES_Key_Init"},
    {"offset": 0x406090, "length": 45, "id": "UserAgent_String"},
]

def extract_decrypted_malware_strings(binary_path: str, rootfs_path: str) -> None:
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DISABLED)
    
    # Internal decryption function boundaries: decrypt_string(char *enc_data, int len, char *out_buf)
    DECRYPT_FUNC_ENTRY = 0x401820
    DECRYPT_FUNC_EXIT  = 0x401895
    OUTPUT_BUFFER_ADDR = 0x7FFF8000 # Scratch buffer for decrypted output
    
    decrypted_config = {}
    
    print(f"[*] Starting targeted emulation of string decryptor @ 0x{DECRYPT_FUNC_ENTRY:08x}...")
    
    for record in ENCRYPTED_STRING_RECORDS:
        enc_addr = record["offset"]
        enc_len = record["length"]
        label = record["id"]
        
        # Set up function arguments according to System V AMD64 ABI:
        # RDI = encrypted_buffer_ptr, RSI = length, RDX = output_buffer_ptr
        ql.arch.regs.rdi = enc_addr
        ql.arch.regs.rsi = enc_len
        ql.arch.regs.rdx = OUTPUT_BUFFER_ADDR
        
        # Set stack pointer and return address
        ql.arch.regs.rsp = 0x7FFFF000
        
        # Execute only the decryption function
        ql.run(begin=DECRYPT_FUNC_ENTRY, end=DECRYPT_FUNC_EXIT)
        
        # Read decrypted plaintext string from output buffer
        decrypted_bytes = ql.mem.read(OUTPUT_BUFFER_ADDR, enc_len)
        # Strip null bytes and decode
        plaintext = decrypted_bytes.split(b"\x00")[0].decode("latin-1")
        
        decrypted_config[label] = plaintext
        print(f"  [+] Decrypted [{label}]: '{plaintext}'")
        
    print("=" * 60)
    print("[*] Complete Extracted Configuration:")
    for k, v in decrypted_config.items():
        print(f"    {k.ljust(20)}: {v}")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/malware_obfuscated"
    ROOTFS = "rootfs/x8664_linux"
    extract_decrypted_malware_strings(TARGET, ROOTFS)
