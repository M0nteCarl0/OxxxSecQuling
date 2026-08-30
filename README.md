# ⚡️ Qiling Framework: Advanced Binary Emulation & Instrumentation Playbook

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Qiling Framework](https://img.shields.io/badge/Qiling-1.4.6-green.svg)](https://github.com/qilingframework/qiling)
[![Cross-Architecture](https://img.shields.io/badge/Arch-ARM%20%7C%20ARM64%20%7C%20MIPS%20%7C%20x86%20%7C%20x86__64%20%7C%20RISC--V-orange.svg)](https://github.com/qilingframework/qiling)
[![Multi-OS](https://img.shields.io/badge/OS-Linux%20%7C%20Windows%20%7C%20macOS%20%7C%20UEFI%20%7C%20DOS%20%7C%20FreeRTOS-purple.svg)](https://github.com/qilingframework/qiling)
[![Telegram Channel](https://img.shields.io/badge/Telegram-OxxxSec-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/OxxxSec)
[![Tests Passing](https://img.shields.io/badge/tests-30%2F30%20passed-brightgreen.svg)](verify_all.py)

A comprehensive, publication-ready technical playbook and **30-part Telegram post series** exploring practical binary analysis, reverse engineering, IoT firmware emulation, vulnerability research, and malware sandboxing using the [Qiling Framework](https://github.com/qilingframework/qiling).

> 📢 **Telegram Channel**: Follow [@OxxxSec](https://t.me/OxxxSec)!

---

## 📑 Table of Contents (30-Part Master Series)

| # | Topic & Directory | Core Emulation / Analysis Focus |
|:---:|:---|:---|
| **01** | [01_universal_cross_arch_sandboxing](01_universal_cross_arch_sandboxing/) | Multi-architecture ELF loading (ARM on x86_64), rootfs containment, execution timeouts |
| **02** | [02_kernel_syscall_interception](02_kernel_syscall_interception/) | Syscall dispatching (`sys_openat`, `sys_read`), argument mutation, and path spoofing |
| **03** | [03_precision_memory_mapping](03_precision_memory_mapping/) | Granular virtual memory layout (`ql.mem.map`), struct serialization, and memory permissions |
| **04** | [04_posix_libc_function_hooking](04_posix_libc_function_hooking/) | Intercepting libc APIs, anti-debug neutralization (`ptrace`), deterministic PRNG (`rand`) |
| **05** | [05_windows_pe_malware_sandboxing](05_windows_pe_malware_sandboxing/) | Win32 PE emulation on Linux/macOS, PEB/TEB initialization, `VirtualAlloc`, Registry APIs |
| **06** | [06_vfs_redirection_mock_devices](06_vfs_redirection_mock_devices/) | Virtual Filesystem (`fs_mapper`), `/proc/cpuinfo` mocking, dynamic character device drivers |
| **07** | [07_raw_shellcode_emulation](07_raw_shellcode_emulation/) | Headerless bytecode execution (`code=...`), stack setup, memory write watchpoint tracing |
| **08** | [08_iot_router_nvram_mocking](08_iot_router_nvram_mocking/) | Embedded MIPS router `httpd` emulation, mocking `libnvram` (`nvram_get`, `nvram_set`) |
| **09** | [09_microsecond_snapshot_restore](09_microsecond_snapshot_restore/) | In-memory checkpointing (`ql.save`, `ql.restore`) for ultra-high-speed fuzzing loops |
| **10** | [10_aflplusplus_cross_arch_fuzzing](10_aflplusplus_cross_arch_fuzzing/) | AFL++ integration (`ql.fuzz`) with Unicornafl persistent mode and coverage bitmap |
| **11** | [11_interactive_gdb_ida_debugging](11_interactive_gdb_ida_debugging/) | Embedded GDB Remote Serial Protocol (RSP) stub for IDA Pro, Ghidra, and Binary Ninja |
| **12** | [12_uefi_dxe_smm_firmware_analysis](12_uefi_dxe_smm_firmware_analysis/) | UEFI DXE driver sandbox, NVRAM variable services (`GetVariable`), protocol DB mocking |
| **13** | [13_automated_unpacking_oep_dumper](13_automated_unpacking_oep_dumper/) | Instruction-level code hooking, detecting tail jumps to OEP, live memory dumping |
| **14** | [14_dynamic_string_decryption](14_dynamic_string_decryption/) | Targeted function emulation, automated decryption loops, malware config extraction |
| **15** | [15_memory_watchpoints_taint_tracing](15_memory_watchpoints_taint_tracing/) | Software memory watchpoints, data-flow tracking, UAF and memory corruption detection |
| **16** | [16_hardware_mmio_peripheral_emulation](16_hardware_mmio_peripheral_emulation/) | Bare-metal MMIO register virtualization (`map_mmio`), UART and hardware timer polling |
| **17** | [17_multi_threading_pthreads_emulation](17_multi_threading_pthreads_emulation/) | Concurrency scheduling, POSIX `pthread_create`, Win32 `CreateThread`, mutex tracing |
| **18** | [18_bypassing_anti_analysis_timing](18_bypassing_anti_analysis_timing/) | Defeating `RDTSC` time-deltas, `CPUID` vendor spoofing, `/proc/self/status` TracerPid |
| **19** | [19_macos_macho_binary_emulation](19_macos_macho_binary_emulation/) | Apple Mach-O (ARM64/x64) execution on Linux/Windows, `dyld`, BSD syscalls, LibSystem |
| **20** | [20_legacy_16bit_dos_mbr_emulation](20_legacy_16bit_dos_mbr_emulation/) | 16-bit real-mode MS-DOS COM & MBR bootkit emulation, `INT 21h` software interrupts |
| **21** | [21_cross_arch_code_coverage_drcov](21_cross_arch_code_coverage_drcov/) | Basic block tracing (`ql.hook_block`), exporting DynamoRIO `.drcov` for IDA Lighthouse |
| **22** | [22_custom_qiling_extensions_plugins](22_custom_qiling_extensions_plugins/) | Modular architecture, subclassing `QilingExtension`, structured API telemetry logger |
| **23** | [23_virtual_network_socket_c2_simulation](23_virtual_network_socket_c2_simulation/) | In-memory socket emulation (`connect`, `send`, `recv`), virtual C2 beacon command injection |
| **24** | [24_dynamic_binary_patching_hijacking](24_dynamic_binary_patching_hijacking/) | In-memory byte patching (`ql.patch`), NOPing license branches, CPU flag manipulation |
| **25** | [25_direct_function_calling_symbols](25_direct_function_calling_symbols/) | Invoking exported `.so` / `.dll` functions directly with Python arguments (`function_call`) |
| **26** | [26_freertos_cortex_m_emulation](26_freertos_cortex_m_emulation/) | Bare-metal FreeRTOS on Cortex-M, task lifecycle, inter-task queue sniffing (`xQueueSend`) |
| **27** | [27_cryptographic_key_extraction](27_cryptographic_key_extraction/) | Hooking crypto key scheduling APIs (`AES_set_encrypt_key`), extracting 256-bit keys |
| **28** | [28_deobfuscating_control_flow_flattening](28_deobfuscating_control_flow_flattening/) | Tracing dispatcher basic blocks, recording state variables, recovering genuine CFGs |
| **29** | [29_windows_registry_com_virtualization](29_windows_registry_com_virtualization/) | In-memory `.reg` hives, persistence detection (`Run` keys), COM object instantiation |
| **30** | [30_headless_malware_triage_pipeline](30_headless_malware_triage_pipeline/) | End-to-end headless triage engine producing structured JSON threat intelligence IOCs |

---

## 🚀 Quick Start

### 1. Automated Environment Setup

Use the built-in bootstrap script for your platform:

#### Windows PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_env.ps1
```

#### Windows Command Prompt (CMD):
```cmd
setup_env.bat
```

#### Linux / macOS / WSL:
```bash
chmod +x setup_env.sh
./setup_env.sh
```

---

### 2. Manual Environment Setup

If you prefer configuring your virtual environment manually:

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install --no-cache-dir -r requirements.txt

# 4. Verify installation
python verify_all.py
```

---

### 3. Provisioning Test Data & RootFS

To download the official multi-architecture `rootfs` datasets (`arm_linux`, `x86_windows`, `mips32el_linux`, `x8664_efi`, `dos`, etc.):

```bash
python download_test_data.py
```

---

## 🧪 Running Examples & Verification

To execute and verify all 30 implementations simultaneously:

```bash
python verify_all.py
```

To run a specific post's implementation:

```bash
# Example: Post 07 (Raw Shellcode Emulation & Staged Decoding)
python 07_raw_shellcode_emulation/example.py

# Example: Post 03 (Precision Memory Mapping & Struct Layout)
python 03_precision_memory_mapping/example.py
```

---

## 📁 Repository Organization

```text
.
├── 01_universal_cross_arch_sandboxing/       # Post 01: Multi-Arch ELF Loading & Sandboxing
│   ├── README.md                             # Markdown post formatted for Telegram
│   └── example.py                            # Standalone, runnable Python implementation
│
├── 02_kernel_syscall_interception/           # Post 02: Syscall Hooking & Dispatching
│   ├── README.md
│   └── example.py
│
├── ...                                       # Posts 03 to 29
│
├── 30_headless_malware_triage_pipeline/      # Post 30: End-to-End Headless Triage Pipeline
│   ├── README.md
│   └── example.py
│
├── qiling_telegram_posts_series.md           # Consolidated master collection (all 30 posts)
├── requirements.txt                          # Python dependencies list
├── setup_env.ps1                             # PowerShell automated setup script
├── setup_env.bat                             # Windows Batch automated setup script
├── setup_env.sh                              # Unix/macOS Shell automated setup script
├── download_test_data.py                     # RootFS & sample binary downloader
└── verify_all.py                             # Health-check & validation test suite
```

---
## 👤 Author & Telegram Channel

- **Official Channel**: [OxxxSec Telegram Channel](https://t.me/OxxxSec) (`@OxxxSec`)
- **Topics**: Daily binary analysis, reverse engineering write-ups, vulnerability research, and firmware sandboxing.

---

## 🔗 References & Ecosystem

- **Qiling Framework Repository**: [https://github.com/qilingframework/qiling](https://github.com/qilingframework/qiling)
- **Qiling Official Documentation**: [https://docs.qiling.io/](https://docs.qiling.io/)
- **Unicorn Engine**: [https://www.unicorn-engine.org/](https://www.unicorn-engine.org/)
- **Capstone Engine**: [https://www.capstone-engine.org/](https://www.capstone-engine.org/)
- **Keystone Assembler**: [https://www.keystone-engine.org/](https://www.keystone-engine.org/)
- **AFLplusplus**: [https://github.com/AFLplusplus/AFLplusplus](https://github.com/AFLplusplus/AFLplusplus)

---

## ⚖️ License & Ethical Notice

This repository is provided for educational, defensive security engineering, vulnerability research, and authorized security auditing purposes only. Ensure you have explicit authorization before analyzing or emulating third-party proprietary software or firmware.
