#!/usr/bin/env bash
# ==============================================================================
# Question 7: File Reorganization Script
# ==============================================================================

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$DIR/reorganized"

# Clean and prepare directory
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

# Extract archive
unzip -q "$DIR/files_to_reorganize.zip" -d "$WORK_DIR"

cd "$WORK_DIR"

# Step 1 & 2: Process files safely handling spaces, Unicode, and Windows CRLF
find . -type f -name "*.txt" | while IFS= read -r file; do
  # Extract category from first matching line
  category=$(grep -m 1 "^category:" "$file" | cut -d' ' -f2- | tr -d '\r')
  mkdir -p "$category"

  # Convert path: remove leading ./ and replace / with -
  relpath=$(echo "$file" | sed 's|^./||')
  newname=$(echo "$relpath" | tr '/' '-')

  # Move file to category directory
  mv "$file" "$category/$newname"
done

# Step 3: Clean up empty directories
find . -type d -empty -delete

# Step 4: Generate and display verification hash
echo "Verification Hash (with README.md):"
find . -type f | LC_ALL=C sort | sha256sum | awk '{print $1}'

echo "Verification Hash (if README.md excluded):"
find . -type f | grep -v "README.md" | LC_ALL=C sort | sha256sum | awk '{print $1}'
