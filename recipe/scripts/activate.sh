#!/usr/bin/env sh

# Store existing env vars and set to this conda env
# so other installs don't pollute the environment.

if [ -n "$GEOMETRIC_DATA_DIR" ]; then
    export _CONDA_SET_GEOMETRIC_DATA_DIR=$GEOMETRIC_DATA_DIR
fi


export GEOMETRIC_DATA_DIR="${CONDA_PREFIX}/share/geometric_data"
