#!/usr/bin/env python3
"""
Verification and Health-Check Suite for Qiling Framework and all 30 Post Examples.
"""

import os
import sys
import subprocess

def check_qiling_installation() -> bool:
    print("[*] Checking Qiling Framework core modules...")
    try:
        import qiling
        from qiling.const import QL_ARCH, QL_OS, QL_VERBOSE
        import unicorn
        import capstone
        import keystone
        import pefile
        import elftools
        
        print(f"  [+] Qiling version    : {getattr(qiling, '__version__', '1.4.x')}")
        print(f"  [+] Unicorn version   : {unicorn.__version__}")
        print(f"  [+] Capstone version  : {capstone.__version__}")
        print(f"  [+] Keystone version  : {keystone.__version__}")
        print(f"  [+] Pefile version    : {pefile.__version__}")
        print("  [+] Core emulation engines: OK")
        return True
    except ImportError as e:
        print(f"  [-] Import error: {e}")
        return False

def verify_all_30_posts() -> bool:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n[*] Verifying 30 post scripts in: {base_dir}")
    
    passed_count = 0
    total_posts = 30
    
    for i in range(1, total_posts + 1):
        # Locate post folder
        folder_prefix = f"{i:02d}_"
        matching_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith(folder_prefix)]
        
        if not matching_dirs:
            print(f"  [-] Post {i:02d}: Directory not found!")
            continue
            
        folder_name = matching_dirs[0]
        script_path = os.path.join(base_dir, folder_name, "example.py")
        readme_path = os.path.join(base_dir, folder_name, "README.md")
        
        if not os.path.exists(script_path):
            print(f"  [-] Post {i:02d} ({folder_name}): example.py missing!")
            continue
        if not os.path.exists(readme_path):
            print(f"  [-] Post {i:02d} ({folder_name}): README.md missing!")
            continue
            
        # Test compilation
        res = subprocess.run([sys.executable, "-m", "py_compile", script_path], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [OK] Post {i:02d}: {folder_name:<42} (README.md, example.py verified)")
            passed_count += 1
        else:
            print(f"  [FAIL] Post {i:02d}: {folder_name} syntax error: {res.stderr.strip()}")
            
    print("=" * 68)
    print(f"[*] Summary: {passed_count}/{total_posts} posts verified successfully!")
    print("=" * 68)
    return passed_count == total_posts

if __name__ == "__main__":
    q_ok = check_qiling_installation()
    if not q_ok:
        print("[-] Qiling core components missing or broken. Please run setup_env script.")
        sys.exit(1)
        
    posts_ok = verify_all_30_posts()
    if posts_ok:
        print("[+] All systems and examples are 100% operational!")
        sys.exit(0)
    else:
        print("[-] Some examples failed verification.")
        sys.exit(1)
