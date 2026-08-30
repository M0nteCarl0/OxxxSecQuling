# ⚡️ 🌀 Deobfuscating Control-Flow Flattening via Instruction Tracing (Python practice)

Control-Flow Flattening (CFF) (widely popularized by OLLVM, Tigress, and proprietary protectors) destroys natural control flow graphs (CFGs). It breaks basic blocks into fragments, places them inside a giant `switch-case` statement inside an infinite loop, and coordinates execution order using a dispatcher state variable. Static analysis decompilers output an unreadable mess of loops. Qiling allows you to deobfuscate flattened code by dynamically tracing basic block execution, recording state variable transitions, and reconstructing genuine execution flow graphs.

## 🧠 Core Concept
- **Dynamic CFG Recovery**: Trace basic block executions to observe genuine branch transitions regardless of dispatcher indirection.
- **State Variable Tracking**: Monitor the dispatcher register/variable (e.g., `EAX` state counter) across loop iterations.
- **Opaque Predicate Elimination**: Dynamically identify dead branches that are never executed during runtime.
- **Symbolic-Emulation Hybrid Tracing**: Combine instruction-level execution logs with control-flow graph reconstructors (NetworkX, Graphviz).
- **Automating Compiler Deobfuscation**: Generate clean patch scripts or microcode passes for IDA Pro / Ghidra based on observed execution traces.

## 💻 Implementation Example
```python
#!/usr/bin/env python3
"""
Post 28: Deobfuscating Control-Flow Flattening via Instruction Tracing
Tracing state variable mutations in flattened code blocks and extracting genuine basic block execution order.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

# Address boundaries of the flattened function
FUNC_BASE = 0x401000
FUNC_END  = 0x401600
DISPATCHER_BLOCK_ADDR = 0x401050

execution_trace = []
state_history = []

def trace_flattened_blocks(ql: Qiling, address: int, size: int) -> None:
    # Filter trace to target function address space
    if FUNC_BASE <= address < FUNC_END:
        # Check if execution reached the central dispatcher block
        if address == DISPATCHER_BLOCK_ADDR:
            # Read the current state variable value (stored in EAX/RAX)
            state_val = ql.arch.regs.rax
            state_history.append((hex(address), hex(state_val)))
            print(f"[DISPATCHER HIT] Central Dispatcher 0x{address:08x} -> Next State Variable: 0x{state_val:x}")
        else:
            execution_trace.append(address)

def run_deobfuscator_trace(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Control-Flow Deobfuscator Sandbox for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DISABLED)
    
    # Hook basic block entries
    ql.hook_block(trace_flattened_blocks)
    
    print("[*] Running obfuscated function to capture true execution path...")
    try:
        ql.run(begin=FUNC_BASE, end=FUNC_END)
    except Exception:
        pass
        
    print("=" * 60)
    print(f"[+] Trace Complete: Captured {len(execution_trace)} basic blocks and {len(state_history)} state transitions.")
    print("[+] Recovered True Execution Order:")
    for idx, (disp, state) in enumerate(state_history[:10]):
        print(f"    Step {idx + 1:02d}: State Var = {state}")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/ollvm_flattened_app"
    ROOTFS = "rootfs/x8664_linux"
    run_deobfuscator_trace(TARGET, ROOTFS)
```

## 🔥 Use Cases
- Defeating OLLVM, Hikari, and Tigress control-flow flattening in protected malware.
- Reconstructing clean Control Flow Graphs (CFGs) for Ghidra / IDA Pro decompilers.
- Identifying and removing opaque predicates and unreachable dead code blocks.
- Auditing commercial software protected by aggressive anti-tamper virtualizers.
- Extracting genuine cryptographic routines concealed inside flattened dispatcher loops.

## ⚠️ Caveats & Responsible Practice
- **Multiple Code Paths**: Dynamic tracing captures only the executed path; feed diverse input testcases to reconstruct complete CFG branches.
- **State Variable Location**: The dispatcher state variable may reside in a CPU register (`EAX`), a stack local variable (`[RBP - 0x10]`), or a global memory pointer.
- **Loop Boundaries**: Specify precise `begin` and `end` addresses to prevent tracing runtime libraries (`libc.so`).
- **Graph Generation**: Export captured trace lists to DOT/Graphviz format for intuitive visual analysis.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: [x86_64 Linux RootFS](https://github.com/qilingframework/rootfs/tree/master/x8664_linux)
- **OLLVM Obfuscated Test Binaries**: [Qiling Deobfuscation Samples](https://github.com/qilingframework/qiling/tree/master/examples/deobfuscation)
- **Control Flow Trace Visualizer**: [NetworkX Graph Analysis](https://networkx.org/)
## 🔗 Resources
- Deobfuscating Control Flow Flattening (https://blog.quarkslab.com/deobfuscation-recovering-an-ollvm-protected-program.html)
- OLLVM Source Code (https://github.com/obfuscator-llvm/obfuscator)

#Qiling #Deobfuscation #OLLVM #ControlFlowFlattening #ReverseEngineering #BinaryAnalysis #CyberSecurity #Python
