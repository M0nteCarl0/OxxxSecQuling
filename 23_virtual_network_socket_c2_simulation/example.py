#!/usr/bin/env python3
"""
Post 23: Virtual Network Socket Simulation & C2 Traffic Interception
Intercepting network beacons from an emulated botnet binary and responding with mock C2 commands.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
import struct

# Simulated C2 Server Tasking Packet
MOCK_C2_TASK = b"CMD:SLEEP:60;REPORT_STATUS=OK;\x00"

def hook_connect(ql: Qiling) -> int:
    sockfd = ql.os.function_arg(0)
    addr_ptr = ql.os.function_arg(1)
    addrlen = ql.os.function_arg(2)
    
    # Read sockaddr_in struct: family (2 bytes), port (2 bytes Big-Endian), IP (4 bytes)
    sockaddr_raw = ql.mem.read(addr_ptr, 8)
    family, port_be, ip_int = struct.unpack(">HH4s", sockaddr_raw[:8])
    ip_str = ".".join(str(b) for b in ip_int)
    
    print(f"[NETWORK] connect(sockfd={sockfd}, IP={ip_str}, Port={port_be}) -> SPOOFING SUCCESS (0)")
    # Return 0 (Connection Established successfully)
    return 0

def hook_send(ql: Qiling) -> int:
    sockfd = ql.os.function_arg(0)
    buf_ptr = ql.os.function_arg(1)
    length = ql.os.function_arg(2)
    
    # Capture raw transmitted beacon data
    sent_data = ql.mem.read(buf_ptr, length)
    print(f"[C2 BEACON CAPTURED] Transmitted {length} bytes: {sent_data.hex()} (ASCII: {sent_data})")
    return length

def hook_recv(ql: Qiling) -> int:
    sockfd = ql.os.function_arg(0)
    buf_ptr = ql.os.function_arg(1)
    maxlen = ql.os.function_arg(2)
    
    # Inject our mock C2 tasking packet into the binary's receive buffer
    response = MOCK_C2_TASK[:maxlen]
    ql.mem.write(buf_ptr, response)
    print(f"[C2 RESPONSE INJECTED] Sent {len(response)} bytes of mock tasking to malware.")
    return len(response)

def run_network_sandbox(binary_path: str, rootfs_path: str) -> None:
    print(f"[*] Initializing Isolated Network Sandbox for {binary_path}...")
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.ARM, verbose=QL_VERBOSE.DEFAULT)
    
    # Hook POSIX network APIs
    ql.os.set_api("connect", hook_connect)
    ql.os.set_api("send", hook_send)
    ql.os.set_api("recv", hook_recv)
    
    print("[*] Running malware with virtualized C2 network layer...")
    ql.run()

if __name__ == "__main__":
    TARGET = "rootfs/arm_linux/bin/botnet_client"
    ROOTFS = "rootfs/arm_linux"
    run_network_sandbox(TARGET, ROOTFS)
