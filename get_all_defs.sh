#!/usr/bin/env bash

# Runs the js definition downloader on all the data files.
# Puts definitions in data/*.def

set -euo pipefail

for file in data/*.data; do
    node get_definitions.js "$file" \
        1> >(tee data/"$(basename "$file")".def) \
        2> >(tee data/"$(basename "$file")".err >&2)
done
