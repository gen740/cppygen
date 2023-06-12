#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Generate python stubs
cd $SCRIPT_DIR/build && stubgen -p pyshell -o $SCRIPT_DIR/python/stubs
