#!/usr/bin/env bash

set -euo pipefail

cat data/*.def | dictfmt \
    -c5 \
    --utf8 \
    --allchars \
    -u urbandictionary.com \
    -s 'Urban Dictionary' \
    --columns \
    -1 \
    ud

dictzip ud.dict
