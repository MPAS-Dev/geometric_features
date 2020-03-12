#!/usr/bin/env sh

# Restore previous env vars if they were set.
unset GEOMETRIC_DATA_DIR
if [ -n "$_CONDA_SET_GEOMETRIC_DATA_DIR" ]; then
    export GEOMETRIC_DATA_DIR=$_CONDA_SET_GEOMETRIC_DATA_DIR
    unset _CONDA_SET_GEOMETRIC_DATA_DIR
fi
