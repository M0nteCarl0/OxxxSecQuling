#!/usr/bin/env python3
"""
Post 17: Multi-Threading & Thread Emulation in Qiling
Emulating a multi-threaded Linux binary, tracing mutex locks, and intercepting worker thread execution.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS

def hook_pthread_create(ql: Qiling) -> int:
    thread_ptr = ql.os.function_arg(0)
    attr_ptr = ql.os.function_arg(1)
    start_routine = ql.os.function_arg(2)
    arg_ptr = ql.os.function_arg(3)
    
    print(f"[THREAD CREATION] pthread_create() -> Worker Function: 0x{start_routine:08x}, Context Arg: 0x{arg_ptr:08x}")
    # Let Qiling's native pthread manager handle the thread creation
    return ql.os.posix.pthread.pthread_create(thread_ptr, attr_ptr, start_routine, arg_ptr)

def hook_pthread_mutex_lock(ql: Qiling) -> int:
    mutex_addr = ql.os.function_arg(0)
    current_tid = getattr(ql.os.thread_management, "cur_thread", None)
    print(f"[MUTEX LOCK] Thread TID={current_tid} acquired mutex at 0x{mutex_addr:08x}")
    return 0 # SUCCESS

def run_multithreaded_sandbox(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Multi-Threaded Sandbox for {binary_path}...")
    ql = Qiling(
        argv=[binary_path],
        rootfs=rootfs_path,
        ostype=QL_OS.LINUX,
        archtype=QL_ARCH.X8664,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Intercept pthread management calls
    ql.os.set_api("pthread_create", hook_pthread_create)
    ql.os.set_api("pthread_mutex_lock", hook_pthread_mutex_lock)
    
    print("[*] Starting multi-threaded binary execution...")
    try:
        ql.run()
        print("[+] All threads completed successfully.")
    except Exception as err:
        print(f"[-] Execution stopped: {err}")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/multithread_worker"
    ROOTFS = "rootfs/x8664_linux"
    run_multithreaded_sandbox(TARGET, ROOTFS)
