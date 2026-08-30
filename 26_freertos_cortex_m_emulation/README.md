# ⚡️ ⏱ FreeRTOS & Bare-Metal Cortex-M RTOS Emulation (Python practice)

Modern IoT microcontrollers, medical devices, and industrial sensors rarely run full Linux operating systems. Instead, they run Real-Time Operating Systems (RTOS) like FreeRTOS on bare-metal ARM Cortex-M processors. Emulating FreeRTOS binaries is uniquely challenging due to task queues, timer callbacks, priority-based preemptive scheduling, and direct hardware interrupt service routines (ISRs). Qiling provides specialized RTOS emulation (`QL_OSTYPE.FREERTOS`), enabling researchers to emulate FreeRTOS task schedulers and intercept inter-task queue communications.

## 🧠 Core Concept
- **RTOS Engine (`QL_OSTYPE.FREERTOS`)**: Emulates FreeRTOS kernel data structures, Task Control Blocks (TCBs), and task context switches.
- **Inter-Task Queue Mocking**: Intercept `xQueueSend`, `xQueueReceive`, and `xQueueCreate` to inspect data exchanged between concurrent RTOS tasks.
- **Task Lifecycle Tracing**: Monitor task creation (`xTaskCreate`), priorities, stack high-water marks, and task states (Running, Ready, Blocked, Suspended).
- **Software Timer Emulation**: Emulate FreeRTOS timer services (`xTimerCreate`, `xTimerStart`) without hardware RTC chips.
- **Firmware Vulnerability Discovery**: Hunt memory corruption vulnerabilities in proprietary RTOS networking stacks (e.g., FreeRTOS+TCP, LwIP).

## 💻 Implementation Example
```python
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
```

## 🔥 Use Cases
- Vulnerability research in automotive microcontroller firmware and drone flight controllers.
- Auditing proprietary industrial IoT firmware running FreeRTOS, Zephyr, or VxWorks.
- Fuzzing embedded RTOS network stacks (FreeRTOS-TCP, MQTT parsers, CoAP endpoints).
- Extracting hardcoded wireless pairing keys (BLE, Zigbee) exchanged across RTOS tasks.
- Validating memory isolation and stack overflow protections in safety-critical medical devices.

## ⚠️ Caveats & Responsible Practice
- **Vector Table Layout**: Bare-metal ARM Cortex-M images require vector tables (Initial SP, Reset Handler) mapped at `0x00000000` or `0x08000000`.
- **Scheduler Ticks**: FreeRTOS relies on SysTick interrupts; Qiling provides virtual tick advancement during task switching.
- **Context Saving**: FreeRTOS uses hardware floating-point registers (FPU) on Cortex-M4/M7; ensure FPU emulation is active if using floating-point math.
- **Task Stack Boundaries**: Stack overflow detection hooks can be attached to FreeRTOS stack limit addresses.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: Bare-Metal FreeRTOS (No rootfs required)
- **Sample FreeRTOS ARM Cortex-M Image**: [sensor_node.bin Sample](https://github.com/qilingframework/qiling/tree/master/examples/freertos)
- **FreeRTOS Kernel Emulation**: [qiling/os/freertos/](https://github.com/qilingframework/qiling/tree/master/qiling/os/freertos)
## 🔗 Resources
- Qiling FreeRTOS Architecture (https://docs.qiling.io/en/latest/freertos/)
- FreeRTOS Kernel Reference Manual (https://www.freertos.org/Documentation/RTOS_book.html)

#Qiling #FreeRTOS #CortexM #IoT #FirmwareSecurity #EmbeddedSystems #VulnerabilityResearch #CyberSecurity
