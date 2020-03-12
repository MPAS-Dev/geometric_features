#!/usr/bin/env csh

# Store existing env vars and set to this conda env
# so other installs don't pollute the environment.

if ( $?GEOMETRIC_DATA_DIR ) then
  setenv _CONDA_SET_GEOMETRIC_DATA_DIR "$GEOMETRIC_DATA_DIR"
endif

setenv GEOMETRIC_DATA_DIR "${CONDA_PREFIX}/share/geometric_data"
