# ⚡️ 🔌 Hardware MMIO & Peripheral Emulation with Qiling (Python practice)

Bare-metal firmware (e.g., ARM Cortex-M, automotive ECUs, industrial PLCs) interacts directly with physical hardware peripherals by reading and writing Memory-Mapped I/O (MMIO) register addresses. In standard emulators, the first time firmware queries a UART status register, hardware timer, or GPIO pin, it hangs in an infinite polling loop waiting for hardware flags that never change. Qiling provides `ql.mem.map_mmio()`, allowing researchers to map virtual peripheral address spaces and attach Python read/write callback handlers to simulate real hardware.

## 🧠 Core Concept
- **MMIO Virtualization (`ql.mem.map_mmio()`)**: Map physical microcontroller address spaces (e.g., `0x40000000 - 0x40010000`) with Python callback dispatchers.
- **UART Serial Port Simulation**: Intercept transmitted characters and feed mock serial commands to the firmware's input buffer.
- **Hardware Register Status Spoofing**: Return expected status bits (e.g., `UART_TX_READY`, `TIMER_EXPIRED`, `PLL_LOCKED`) to unblock hardware initialization loops.
- **Interrupt Injection**: Trigger simulated hardware interrupts (IRQs) upon peripheral timer expiration or packet arrival.
- **Hardware-Independent Firmware Auditing**: Run real IoT / automotive firmware binaries on standard x86 workstations without hardware rigs.

## 💻 Implementation Example
```python
#!/usr/bin/env python3
"""
Post 16: Hardware MMIO & Peripheral Emulation
Emulating an ARM Cortex-M micro-controller UART peripheral and watchdog timer MMIO range.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import struct

# Simulated Hardware Register Offsets for UART Peripheral (Base: 0x4000C000)
UART_DR   = 0x00  # Data Register (Read RX / Write TX)
UART_FR   = 0x18  # Flag Register (Status bits)
UART_IBRD = 0x24  # Baud Rate Register

# Flag Register bitmask constants
UART_FR_TXFF = (1 << 5) # Transmit FIFO Full
UART_FR_RXFE = (1 << 4) # Receive FIFO Empty
UART_FR_TXFE = (1 << 7) # Transmit FIFO Empty

def uart_mmio_read(ql: Qiling, offset: int, size: int) -> int:
    # Firmware is checking UART status flag register
    if offset == UART_FR:
        # Return TXFE (Transmit FIFO Empty) so firmware knows UART is ready to transmit
        return UART_FR_TXFE
    elif offset == UART_DR:
        # Simulate an incoming character 'K' from serial console
        print("[MMIO UART] Firmware read received byte: 'K'")
        return ord("K")
    return 0

def uart_mmio_write(ql: Qiling, offset: int, size: int, value: int) -> None:
    if offset == UART_DR:
        char_val = chr(value & 0xFF)
        print(f"[MMIO UART TX] Firmware transmitted: '{char_val}' (0x{value:02x})")
    elif offset == UART_IBRD:
        print(f"[MMIO UART CONFIG] Baud rate divisor set to: {value}")

def run_cortex_m_mmio_sandbox(binary_path: str) -> None:
    print(f"[*] Initializing Bare-Metal ARM Cortex-M Sandbox for {binary_path}...")
    ql = Qiling(
        argv=[binary_path],
        rootfs="", # Bare-metal: no Linux rootfs needed
        ostype=QL_OS.LINUX,
        archtype=QL_ARCH.ARM,
        verbose=QL_VERBOSE.DEFAULT
    )
    
    # Map UART Peripheral MMIO range: 0x4000C000 (Size 4KB)
    UART_BASE = 0x4000C000
    MMIO_SIZE = 0x1000
    
    ql.mem.map_mmio(UART_BASE, MMIO_SIZE, uart_mmio_read, uart_mmio_write, info="[Virtual_UART0]")
    print(f"[+] Mapped Virtual UART MMIO at 0x{UART_BASE:08x}")
    
    print("[*] Running bare-metal firmware with active MMIO emulation...")
    try:
        ql.run(count=100000) # Execute 100k instructions
    except Exception as err:
        print(f"[*] Emulation boundary: {err}")

if __name__ == "__main__":
    TARGET = "rootfs/arm_baremetal/firmware.bin"
    run_cortex_m_mmio_sandbox(TARGET)
```

## 🔥 Use Cases
- Emulating automotive CAN bus controllers and engine management firmware (ECUs).
- Overcoming endless register polling loops during IoT device boot sequences.
- Simulating industrial Modbus/Profibus fieldbus controller peripherals.
- Auditing embedded hardware crypto engines (AES/SHA accelerators) via MMIO registers.
- Fuzzing bare-metal RTOS drivers with mutated hardware response packets.

## ⚠️ Caveats & Responsible Practice
- **Page Alignment**: MMIO base addresses must align to 4096-byte (4KB) boundaries.
- **Register Widths**: Firmware might read MMIO registers using 8-bit, 16-bit, or 32-bit instructions; ensure callbacks handle varying `size` parameters.
- **Unimplemented Offsets**: Log unhandled register offsets to identify missing peripheral features when firmware fails to initialize.
- **Bare-Metal Memory**: For raw binary dumps without ELF headers, manually map RAM and Flash regions using `ql.mem.map()` before starting.

## 📦 Test Data & Sample Binaries
- **Target Architecture RootFS**: Bare-Metal Firmware (Zero OS RootFS required)
- **Sample Microcontroller Firmware**: [ARM Cortex-M Firmware Sample (.bin)](https://github.com/qilingframework/qiling/tree/master/examples/arm_baremetal)
- **MMIO Emulation Engine**: [qiling/arch/arm.py](https://github.com/qilingframework/qiling/blob/master/qiling/arch/arm.py)
## 🔗 Resources
- Qiling MMIO API Reference (https://docs.qiling.io/en/latest/memory/#mmio)
- ARM Cortex-M Memory Map Specification (https://developer.arm.com/documentation/dui0552/a/)

#Qiling #MMIO #HardwareEmulation #BareMetal #ARM #CortexM #FirmwareSecurity #EmbeddedSystems
