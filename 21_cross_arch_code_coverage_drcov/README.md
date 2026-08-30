# ⚡️ 📊 Cross-Architecture Code Coverage Collection: drcov & Lighthouse (Python practice)

When analyzing binaries, developing exploits, or running directed fuzzers, knowing exactly which basic blocks and functions were executed is essential. In GUI disassemblers (IDA Pro, Ghidra, Binary Ninja), plugins like Lighthouse visualize this execution flow with color-coded coverage maps. Qiling includes high-performance basic block tracing (`ql.hook_block()`) and a built-in `coverage` extension capable of exporting standard DynamoRIO `drcov` coverage files across any supported CPU architecture.

## 🧠 Core Concept
- **Basic Block Tracing (`ql.hook_block()`)**: Automatically tracks every executed basic block starting address and instruction length.
- **Standard `drcov` File Generation**: Exports coverage dumps directly compatible with IDA Pro Lighthouse, Ghidra, and Binary Ninja plugins.
- **Cross-Architecture Coverage**: Generate accurate coverage maps for ARM, MIPS, or PPC binaries without needing DynamoRIO or hardware tracing pins.
- **Differential Coverage Analysis**: Compare coverage dumps from different input test cases to isolate conditional branch triggers.
- **Fuzzer Corpus Optimization**: Identify unique code paths to minimize fuzzer testcase corpora efficiently.

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Visualizing explored code paths and unreached functions in IDA Pro / Ghidra using Lighthouse.
- Evaluating unit test and fuzzing branch coverage across cross-compiled embedded binaries.
- Differential binary analysis: identifying which blocks execute during successful vs failed logins.
- Hunting dead code, unreferenced easter eggs, and hidden administrative backdoors.
- Optimizing fuzzing input corpora by eliminating redundant test cases that traverse identical paths.

## ⚠️ Caveats & Responsible Practice
- **Base Address Synchronization**: Ensure the base address in your IDA / Ghidra database matches the ASLR base or load address configured in Qiling.
- **Performance**: Basic block hooking introduces minimal overhead, but disable verbose logging (`QL_VERBOSE.DISABLED`) for maximum tracing speed.
- **Coverage Filtering**: You can filter coverage collection to only include the main binary module and ignore shared libraries (`libc.so`).
- **drcov Header Format**: The output `.drcov` file includes module tables and block lists adhering to DynamoRIO v2 specification.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [ARM Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/arm_linux)
- **Coverage Dumps & Lighthouse Plugin**: [Lighthouse Code Coverage Plugin](https://github.com/gaasedelen/lighthouse)
- **Qiling Coverage Module**: [qiling/extensions/coverage/](https://github.com/qilingframework/qiling/tree/master/qiling/extensions/coverage)
## 🔗 Resources
- Lighthouse IDA / Ghidra Plugin (https://github.com/gaasedelen/lighthouse)
- DynamoRIO drcov Format (https://dynamorio.org/page_drcov.html)

#Qiling #CodeCoverage #Lighthouse #IDAPro #Ghidra #ReverseEngineering #Fuzzing #CyberSecurity
