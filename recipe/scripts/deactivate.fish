#!/usr/bin/env fish

# Restore previous env vars if they were set.
set -e GEOMETRIC_DATA_DIR
if set -q _CONDA_SET_GEOMETRIC_DATA_DIR
    set -gx  GEOMETRIC_DATA_DIR "$_CONDA_SET_GEOMETRIC_DATA_DIR"
    set -e _CONDA_SET_GEOMETRIC_DATA_DIR
end
