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
