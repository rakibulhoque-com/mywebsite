#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Generating CV..."
python "$SCRIPT_DIR/python/generate_cv.py"
echo "Output: $SCRIPT_DIR/RakibulHoque_CV.pdf"
