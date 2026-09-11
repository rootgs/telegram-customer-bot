#!/usr/bin/env sh
set -eu

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. Please install Python 3.11 or newer first."
  exit 1
fi

python3 install.py
