#!/usr/bin/env csh

# Restore previous env vars if they were set.
unsetenv GEOMETRIC_DATA_DIR
if ( $?_CONDA_SET_GEOMETRIC_DATA_DIR ) then
    setenv GEOMETRIC_DATA_DIR "$_CONDA_SET_GEOMETRIC_DATA_DIR"
    unsetenv _CONDA_SET_GEOMETRIC_DATA_DIR
endif
