# ⚡️ 🔑 Automated Cryptographic Key Extraction from Emulated Binaries (Python practice)

Extracting cryptographic keys (AES, RSA, ChaCha20) from compiled binaries is a classic reverse engineering challenge. Obfuscators, white-box wrappers, and anti-tamper protections make static key extraction extraordinarily tedious. However, at runtime, before data can be encrypted or decrypted by standard crypto routines (such as OpenSSL, mbedTLS, or TinyAES), the expanded round keys and initialization vectors (IVs) MUST exist in memory in a usable format. Qiling enables automated, instant key extraction by hooking standard cryptographic function entrypoints.

## 🧠 Core Concept
- **Crypto Function Entry Point Hooking**: Intercept standard crypto initialization routines (`AES_set_encrypt_key`, `mbedtls_aes_setkey_enc`, `EVP_EncryptInit`).
- **Automated Key Parameter Extraction**: Read key length and raw key memory buffers directly from argument registers according to target ABI.
- **Entropy & Key Format Validation**: Verify extracted key entropy in Python to confirm valid 128-bit, 192-bit, or 256-bit symmetric keys.
- **IV & Nonce Interception**: Extract dynamic Initialization Vectors passed alongside cipher keys.
- **Zero Algorithmic Analysis Needed**: Extract cryptographic credentials without reverse engineering complex mathematical transformation matrices.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Recovering AES/ChaCha20 decryption keys from ransomware samples during incident response.
- Extracting TLS session master secrets and pre-shared keys (PSK) from firmware clients.
- Auditing embedded DRM implementations to verify secure key storage compliance.
- Automating decryption of proprietary configuration files and encrypted database blobs.
- Validating cryptographic key entropy and randomness in IoT device firmware.

## ⚠️ Caveats & Responsible Practice
- **Statically Linked Crypto**: If OpenSSL or mbedTLS is statically linked and stripped, identify the key expansion function offset using Ghidra / IDA and hook via `ql.hook_address()`.
- **Inlined Key Expansion**: If crypto is fully inlined, place memory read watchpoints (`ql.hook_mem_read()`) on the AES S-Box table to locate key expansion rounds.
- **Key Lengths**: Standard AES keys are 128 (16 bytes), 192 (24 bytes), or 256 bits (32 bytes).
- **Calling Conventions**: On Windows x64, arguments are passed in `RCX, RDX, R8, R9`; on Linux System V AMD64, `RDI, RSI, RDX, RCX`.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [x86_64 Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/x8664_linux)
- **Sample Encrypted Client**: [Qiling Crypto Test Binaries](https://github.com/qilingframework/qiling/tree/master/examples/crypto)
- **OpenSSL API Hook Stubs**: [qiling/os/posix/syscall/](https://github.com/qilingframework/qiling/tree/master/qiling/os/posix)
## 🔗 Resources
- OpenSSL AES API Reference (https://www.openssl.org/docs/manmaster/man3/AES_encrypt.html)
- mbedTLS Crypto Documentation (https://mbed-tls.readthedocs.io/)

#Qiling #Cryptography #KeyExtraction #AES #ReverseEngineering #MalwareAnalysis #IncidentResponse #CyberSecurity
