#!/usr/bin/env python3
"""
Post 26: FreeRTOS & Bare-Metal Cortex-M RTOS Emulation
Loading a FreeRTOS ARM Cortex-M firmware image and hooking queue operations to inspect inter-task communication.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import struct

def hook_xQueueSend(ql: Qiling) -> int:
    xQueue_handle = ql.os.function_arg(0)
    pvItemToQueue_ptr = ql.os.function_arg(1)
    xTicksToWait = ql.os.function_arg(2)
    
    # Read message data pushed into the queue (e.g. 16 bytes telemetry structure)
    msg_data = ql.mem.read(pvItemToQueue_ptr, 16)
    print(f"[FreeRTOS QUEUE] xQueueSend(Queue=0x{xQueue_handle:08x}, WaitTicks={xTicksToWait})")
    print(f"  -> Message Content (Hex): {msg_data.hex()} | ASCII: {msg_data}")
    
    # pdPASS = 1 (Success in FreeRTOS)
    return 1

def hook_xTaskCreate(ql: Qiling) -> int:
    pxTaskCode = ql.os.function_arg(0)
    pcName_ptr = ql.os.function_arg(1)
    usStackDepth = ql.os.function_arg(2)
    pvParameters = ql.os.function_arg(3)
    uxPriority = ql.os.function_arg(4)
    
    task_name = ql.os.utils.read_cstring(pcName_ptr)
    print(f"[FreeRTOS TASK] Created Task: '{task_name}' | Entry: 0x{pxTaskCode:08x} | Priority: {uxPriority}")
    return 1 # pdPASS

def run_freertos_sandbox(firmware_bin: str) -> None:
    print(f"[*] Initializing FreeRTOS Cortex-M Sandbox for {firmware_bin}...")
    ql = Qiling(
        argv=[firmware_bin],
        rootfs="", # Bare-metal: no Linux rootfs
        ostype=QL_OS.FREERTOS,
        archtype=QL_ARCH.CORTEX_M,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Hook FreeRTOS kernel APIs
    ql.os.set_api("xQueueSend", hook_xQueueSend)
    ql.os.set_api("xTaskCreate", hook_xTaskCreate)
    
    print("[*] Starting FreeRTOS task scheduler emulation...")
    try:
        ql.run(count=200000) # Execute 200k instructions
    except Exception as err:
        print(f"[*] RTOS execution checkpoint: {err}")

if __name__ == "__main__":
    TARGET_FIRMWARE = "rootfs/arm_freertos/sensor_node.bin"
    run_freertos_sandbox(TARGET_FIRMWARE)
