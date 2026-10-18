#!/usr/bin/env bash
# ==============================================================================
# Question 8: Calculate Mumbai Feb 2025 Total Revenue
# ==============================================================================

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure extracted folder exists
if [ ! -f "$DIR/sales_data/sales_data.csv" ]; then
    unzip -q "$DIR/sales_data.zip" -d "$DIR/sales_data"
fi

python3 "$DIR/solution.py"

