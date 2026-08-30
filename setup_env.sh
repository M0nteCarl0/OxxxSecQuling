#!/usr/bin/env bash
# ==============================================================================
# Quick Environment Setup for Qiling Framework (Linux / macOS / WSL)
# ==============================================================================
set -e

echo "============================================================"
echo " 🚀 Qiling Framework Environment Quick Setup"
echo "============================================================"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "[-] python3 could not be found. Please install Python 3.8-3.12."
    exit 1
fi

PYTHON_VER=$(python3 --version)
echo "[+] Found: $PYTHON_VER"

# Create virtual environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment at '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    echo "[+] Virtual environment created."
else
    echo "[+] Virtual environment '$VENV_DIR' already exists."
fi

# Activate and install
source "$VENV_DIR/bin/activate"

echo "[*] Upgrading pip and installing requirements..."
pip install --no-cache-dir -r requirements.txt

echo "[*] Running verification suite..."
python verify_all.py

echo "============================================================"
echo " [✓] Environment setup completed!"
echo " To activate run: source .venv/bin/activate"
echo "============================================================"
