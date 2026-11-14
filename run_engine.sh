#!/bin/bash
cd "$(dirname "$0")"
exec /opt/homebrew/bin/python3 -u main.py 2>> stderr.log