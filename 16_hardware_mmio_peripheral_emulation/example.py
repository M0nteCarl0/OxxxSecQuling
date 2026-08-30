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
