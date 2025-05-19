#!/bin/bash

set -e

TARGET_DIR="../galaxy-umsa.grid.cesnet.cz"

for yml_file in "$TARGET_DIR"/*.yml; do
    echo "Processing $yml_file"
    python3 fix_lockfile.py "$yml_file"
    python3 update_tool.py "$yml_file"
done

echo "All files processed."