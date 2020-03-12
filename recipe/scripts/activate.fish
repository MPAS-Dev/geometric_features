#!/usr/bin/env fish

if set -q GEOMETRIC_DATA_DIR
  set -gx _CONDA_SET_GEOMETRIC_DATA_DIR "$GEOMETRIC_DATA_DIR"
end

set -gx GEOMETRIC_DATA_DIR "$CONDA_PREFIX/share/geometric_data"
