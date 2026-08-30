# ⚡️ 📁 Virtual Filesystem (VFS) Redirection & Mock Device Files (Python practice)

When analyzing closed-source binaries, hardware daemons, or evasion-heavy malware, applications frequently check pseudo-files like `/proc/cpuinfo`, `/proc/self/status`, `/sys/class/net`, or `/dev/urandom`. If these files are missing or contain host data, the guest binary will either crash or detect the analysis environment. Qiling's Virtual Filesystem (VFS) and `ql.os.fs_mapper` allow you to intercept any guest file path and serve dynamic in-memory mock files, virtual devices, or custom Python stream objects without altering host disks.

## 🧠 Core Concept
- **VFS Layering**: Maps guest absolute paths to a clean sandbox directory while allowing granular path-by-path redirection.
- **In-Memory File Mocking**: Create virtual files using `ql.os.fs_mapper.add_virtual_file()` populated with synthetic content generated at runtime.
- **Dynamic Device Drivers**: Emulate character devices (`/dev/crypto`, `/dev/gpio`) with custom Python read/write callbacks.
- **Host Filesystem Isolation**: Guest file writes are trapped in memory or redirected to a scratch directory, preventing accidental destruction of host files.
- **Anti-Analysis Defeat**: Provide spoofed `/proc/version` or `/proc/self/status` (`TracerPid: 0`) to conceal debugging artifacts.

## 💻 Implementation Example
```python
#!/usr/bin/env python3
"""
Post 06: Virtual Filesystem (VFS) Redirection & Mock Device Files
Mocking `/proc/cpuinfo` and `/dev/custom_hw` with custom in-memory file objects.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
from qiling.os.posix.filestruct import ql_file

# Define a dynamic virtual device file with custom Python read/write callbacks
class MockCustomHardwareDevice(ql_file):
    def read(self, size: int) -> bytes:
        print(f"[VFS] Guest binary read {size} bytes from /dev/custom_hw")
        # Return synthetic hardware telemetry packet
        return b"\x01\x02\x03\x04\xAA\xBB\xCC\xDD"
        
    def write(self, data: bytes) -> int:
        print(f"[VFS] Guest binary wrote command to /dev/custom_hw: {data.hex()}")
        return len(data)
        
    def close(self) -> int:
        print("[VFS] /dev/custom_hw closed")
        return 0

def run_vfs_sandbox(binary_path: str, rootfs_path: str) -> None:
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.ARM, verbose=QL_VERBOSE.DEFAULT)
    
    # 1. Mock `/proc/cpuinfo` to simulate a specific embedded ARM SoC
    fake_cpuinfo = (
        "Processor\t: ARMv7 Processor rev 1 (v7l)\n"
        "BogoMIPS\t: 1594.36\n"
        "Features\t: half thumb fastmult vfp edsp neon vfpv3 tls vfpd32\n"
        "CPU architecture: 7\n"
        "Hardware\t: BCM2835\n"
    )
    # Map virtual file in guest space
    ql.os.fs_mapper.add_virtual_file("/proc/cpuinfo", fake_cpuinfo.encode())
    
    # 2. Map custom simulated hardware device node
    ql.os.fs_mapper.add_virtual_file("/dev/custom_hw", MockCustomHardwareDevice())
    
    print("[*] Running binary with Virtual Filesystem mappings active...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/arm_linux/bin/iot_sensor_daemon"
    ROOTFS = "rootfs/arm_linux"
    run_vfs_sandbox(TARGET, ROOTFS)
```

## 🔥 Use Cases
- Emulating IoT firmware daemons that depend on proprietary Linux kernel `/dev/` driver nodes.
- Spoofing `/proc/self/maps` and `/proc/self/status` to bypass anti-tamper and anti-debugging checks.
- Feeding deterministic entropy to binaries reading from `/dev/random` or `/dev/urandom`.
- Simulating network socket files and named FIFOs (`/tmp/comm.fifo`) entirely in memory.
- Intercepting and capturing dropped files created by malware during execution without saving to disk.

## ⚠️ Caveats & Responsible Practice
- **Path Resolution**: Guest paths must be specified as absolute guest paths (e.g., `'/etc/hosts'`), not host filesystem paths.
- **File Mode Inheritance**: When subclassing `ql_file`, implement standard file methods (`read`, `write`, `close`, `lseek`, `ioctl`) if the binary uses advanced I/O.
- **Permissions**: Virtual files are by default readable and writable; adjust file permission attributes if testing access control logic.
- **VFS Mapping Precedence**: Virtual files mapped with `fs_mapper` take precedence over physical files on disk in the `rootfs`.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [ARM Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/arm_linux)
- **Virtual Filesystem Modules**: [qiling/os/posix/filestruct.py](https://github.com/qilingframework/qiling/blob/master/qiling/os/posix/filestruct.py)
- **Procfs & Sysfs Test Data**: [Qiling Procfs Mock Examples](https://github.com/qilingframework/qiling/tree/master/examples/vfs)
## 🔗 Resources
- Qiling VFS Architecture Guide (https://docs.qiling.io/en/latest/vfs/)
- Linux Procfs Specification (https://man7.org/linux/man-pages/man5/proc.5.html)

#Qiling #VFS #VirtualFilesystem #Sandboxing #ReverseEngineering #IoT #FirmwareAnalysis #CyberSecurity
