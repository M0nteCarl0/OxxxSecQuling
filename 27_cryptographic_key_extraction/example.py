#!/usr/bin/env python3
"""
Post 27: Automated Cryptographic Key Extraction from Emulated Binaries
Emulating an encrypted binary and hooking `AES_set_encrypt_key` to automatically extract 256-bit AES keys.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import binascii

extracted_keys = []

def hook_AES_set_encrypt_key(ql: Qiling) -> int:
    userKey_ptr = ql.os.function_arg(0)
    bits = ql.os.function_arg(1)
    key_struct_ptr = ql.os.function_arg(2)
    
    key_bytes_len = bits // 8
    raw_key = ql.mem.read(userKey_ptr, key_bytes_len)
    key_hex = binascii.hexlify(raw_key).decode()
    
    print("=" * 60)
    print(f"[!] CRYPTOGRAPHIC KEY EXTRACTED: AES-{bits}")
    print(f"    Key Memory Address: 0x{userKey_ptr:08x}")
    print(f"    Raw Key (Hex)     : {key_hex}")
    print(f"    Raw Key (Bytes)   : {raw_key}")
    print("=" * 60)
    
    extracted_keys.append({"bits": bits, "hex": key_hex, "raw": raw_key})
    return 0 # 0 indicates SUCCESS in OpenSSL AES API

def run_crypto_extractor(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Automated Crypto Key Extractor for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DISABLED)
    
    # Register API hook on OpenSSL / standard AES key expansion entrypoint
    ql.os.set_api("AES_set_encrypt_key", hook_AES_set_encrypt_key)
    ql.os.set_api("AES_set_decrypt_key", hook_AES_set_encrypt_key)
    
    print("[*] Running binary to trigger cryptographic operations...")
    try:
        ql.run()
    except Exception:
        pass
        
    print(f"[+] Extraction complete: Total {len(extracted_keys)} unique cryptographic key(s) captured.")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/secure_vault_client"
    ROOTFS = "rootfs/x8664_linux"
    run_crypto_extractor(TARGET, ROOTFS)
