#!/usr/bin/env python3
"""
Automated Test Data Downloader & RootFS Provisioner for Qiling Framework Posts.
Clones or downloads official Qiling rootfs environments and sample binaries.
"""

import os
import sys
import subprocess
import urllib.request
import zipfile

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOTFS_DIR = os.path.join(WORKSPACE_DIR, "rootfs")
ROOTFS_REPO_URL = "https://github.com/qilingframework/rootfs/archive/refs/heads/master.zip"

def download_official_rootfs() -> None:
    print("=" * 65)
    print(" 📦 Qiling Framework Official RootFS Downloader")
    print("=" * 65)
    
    if os.path.exists(ROOTFS_DIR) and len(os.listdir(ROOTFS_DIR)) > 2:
        print(f"[+] RootFS directory already exists at: {ROOTFS_DIR}")
        print("[+] Available rootfs architectures:")
        for item in os.listdir(ROOTFS_DIR):
            item_path = os.path.join(ROOTFS_DIR, item)
            if os.path.isdir(item_path):
                print(f"    - {item}")
        return

    os.makedirs(ROOTFS_DIR, exist_ok=True)
    zip_target = os.path.join(WORKSPACE_DIR, "rootfs_master.zip")
    
    print("[*] Downloading official Qiling RootFS archive (~50 MB)...")
    print(f"    Source URL: {ROOTFS_REPO_URL}")
    
    try:
        urllib.request.urlretrieve(ROOTFS_REPO_URL, zip_target)
        print("[+] Download complete! Extracting archive...")
        
        with zipfile.ZipFile(zip_target, "r") as zip_ref:
            zip_ref.extractall(WORKSPACE_DIR)
            
        extracted_folder = os.path.join(WORKSPACE_DIR, "rootfs-master")
        if os.path.exists(extracted_folder):
            for item in os.listdir(extracted_folder):
                src = os.path.join(extracted_folder, item)
                dst = os.path.join(ROOTFS_DIR, item)
                if not os.path.exists(dst):
                    os.rename(src, dst)
            try:
                os.rmdir(extracted_folder)
            except Exception:
                pass
                
        if os.path.exists(zip_target):
            os.remove(zip_target)
            
        print(f"[+] RootFS successfully unpacked to: {ROOTFS_DIR}")
    except Exception as err:
        print(f"[-] Automated download failed: {err}")
        print("[*] Manual installation instructions:")
        print("    1. git clone https://github.com/qilingframework/rootfs.git")
        print(f"    2. Move 'rootfs' folder into: {WORKSPACE_DIR}")

if __name__ == "__main__":
    download_official_rootfs()
