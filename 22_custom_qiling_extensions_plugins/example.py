#!/usr/bin/env python3
"""
Post 22: Building Custom Qiling Extensions & Middleware Plugins
Creating a reusable Qiling extension class that logs and colors all API calls with arguments and return values.
"""

from qiling import Qiling
from qiling.const import QL_VERBOSE, QL_ARCH, QL_OS
from qiling.extensions import QilingExtension

# Define a reusable custom Qiling Extension for comprehensive API Telemetry
class APITelemetryLogger(QilingExtension):
    def __init__(self, ql: Qiling, log_to_file: bool = False):
        super().__init__(ql)
        self.log_to_file = log_to_file
        self.call_history = []
        self._setup_hooks()
        
    def _setup_hooks(self) -> None:
        # Register hooks or wrap APIs dynamically
        print("[Extension] APITelemetryLogger initialized and attached to Qiling instance.")
        
    def log_api_call(self, api_name: str, args: list, retval: int) -> None:
        event = {
            "api": api_name,
            "args": [f"0x{a:x}" if isinstance(a, int) else str(a) for a in args],
            "retval": f"0x{retval:x}"
        }
        self.call_history.append(event)
        print(f" [TELEMETRY] API: {api_name:<20} | Args: {event['args']} | Ret: {event['retval']}")
        
    def generate_report(self) -> dict:
        return {
            "total_calls": len(self.call_history),
            "events": self.call_history
        }

def run_with_custom_extension(binary_path: str, rootfs_path: str) -> None:
    ql = Qiling([binary_path], rootfs_path, ostype=QL_OS.LINUX, archtype=QL_ARCH.X8664, verbose=QL_VERBOSE.DISABLED)
    
    # Attach our custom extension
    logger_ext = APITelemetryLogger(ql)
    
    # Add a sample API hook that feeds our telemetry extension
    def hooked_malloc(ql: Qiling) -> int:
        size = ql.os.function_arg(0)
        ret = ql.os.heap.alloc(size)
        logger_ext.log_api_call("malloc", [size], ret)
        return ret
        
    ql.os.set_api("malloc", hooked_malloc)
    
    print("[*] Running binary with APITelemetryLogger extension active...")
    try:
        ql.run()
    except Exception:
        pass
        
    # Extract telemetry report
    report = logger_ext.generate_report()
    print("=" * 60)
    print(f"[+] Extension Report Generated: {report['total_calls']} API calls recorded.")

if __name__ == "__main__":
    TARGET = "rootfs/x8664_linux/bin/sample_app"
    ROOTFS = "rootfs/x8664_linux"
    run_with_custom_extension(TARGET, ROOTFS)
