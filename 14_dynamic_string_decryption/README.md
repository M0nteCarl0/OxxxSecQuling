# ⚡️ 🔓 Dynamic String Decryption & Malware Config Extraction (Python practice)

Modern malware families (e.g., Cobalt Strike, Emotet, Qakbot, LockBit) rarely leave command-and-control (C2) domains, encryption keys, or API names in plaintext. Instead, they utilize custom string decryption routines (stack strings, rolling XOR, RC4, or custom substitution ciphers) invoked hundreds of times throughout the binary. Rather than manually reimplementing these proprietary algorithms in Python, Qiling allows you to emulate only the target decryption subroutine directly inside the binary and extract all decrypted strings dynamically.

## 🧠 Core Concept
- **Targeted Function Emulation**: Jump directly into a specific internal subroutine address without executing the surrounding malware logic.
- **Automated Iteration over Ciphertext Tables**: Pass encrypted buffers and keys sequentially into the emulated decryption function.
- **Direct Memory Buffer Extraction**: Read decrypted plaintext bytes directly from the return register or output buffer pointer in memory.
- **Zero Algorithm Reimplementation**: No need to spend hours reversing complex assembly math; let the binary decrypt its own strings in Qiling.
- **Batch Configuration Dumping**: Extract hundreds of obfuscated strings (C2 URLs, user-agents, registry keys) in seconds.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Extracting high-fidelity Indicators of Compromise (IOCs) from evasive malware families.
- Decrypting dynamic API hashing tables and imported function strings.
- Recovering embedded encryption keys and IVs used for payload staging or ransomware.
- Automating threat intelligence feeds by batch-processing thousands of daily malware submissions.
- Accelerating manual reverse engineering by resolving string annotations before loading into IDA.

## ⚠️ Caveats & Responsible Practice
- **Global State Initialization**: If the decryption function relies on a global S-Box or key table initialized during binary startup, run the binary up to the initialization point first before snapshotting.
- **Calling Conventions**: Verify target architecture calling conventions (e.g., x86 fastcall / stdcall / cdecl vs x86_64 ABI).
- **Stack Cleanliness**: Reset the stack pointer (`RSP`/`ESP`) between function calls to prevent stack collisions.
- **End Address**: Ensure the `end` parameter marks the exact `RET` instruction of the target function.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [x86_64 Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/x8664_linux)
- **Obfuscated Sample Binaries**: [Qiling Malware Emulation Samples](https://github.com/qilingframework/qiling/tree/master/examples/malware)
- **String Decryptor Harness**: [qiling/os/posix/function.py](https://github.com/qilingframework/qiling/blob/master/qiling/os/posix/function.py)
## 🔗 Resources
- Qiling Function Emulation Guide (https://docs.qiling.io/en/latest/function_call/)
- Malware Config Extraction Techniques (https://forensicanalysis.gitbook.io/malware-analysis/)

#Qiling #MalwareAnalysis #ConfigExtraction #ReverseEngineering #ThreatIntel #Deobfuscation #CyberSecurity #Python
