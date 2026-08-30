#!/usr/bin/env python3
"""
Post 21: Cross-Architecture Code Coverage Collection (drcov / IDA Lighthouse)
Executing target binary, recording executed basic blocks, and exporting `.drcov` file for Ghidra/IDA.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
from qiling.extensions import coverage

def collect_code_coverage(binary_path: str, rootfs_path: str, test_input: str, output_cov_file: str) -> None:
    print(f"[*] Initializing Qiling coverage collection for {binary_path}...")
    ql = Qiling(
        argv=[binary_path, test_input],
        rootfs=rootfs_path,
        ostype=QL_OS.LINUX,
        archtype=QL_ARCH.ARM,
        verbose=QL_VERBOSE.DISABLED
    )
    
    # 1. Initialize Qiling Coverage Extension
    cov = coverage.Coverage(ql)
    
    # 2. Activate drcov output format
    cov.activate(coverage.FORMAT_DRCOV)
    
    print(f"[*] Executing binary with test input: '{test_input}'...")
    try:
        ql.run()
    except Exception as err:
        print(f"[*] Execution finished: {err}")
        
    # 3. Dump coverage data to file
    cov.dump(output_cov_file)
    print(f"[+] Coverage successfully written to '{output_cov_file}'")
    print(f"[+] You can now load '{output_cov_file}' in IDA Pro (Lighthouse plugin) or Ghidra!")

if __name__ == "__main__":
    TARGET = "rootfs/arm_linux/bin/arm_parser"
    ROOTFS = "rootfs/arm_linux"
    OUTPUT_FILE = "coverage_trace.drcov"
    
    collect_code_coverage(TARGET, ROOTFS, "TEST_PAYLOAD_ADMIN_AUTH", OUTPUT_FILE)
