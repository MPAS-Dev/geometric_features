:: Store existing env vars and set to this conda env
:: so other installs don't pollute the environment.

@if defined GEOMETRIC_DATA_DIR (
    set "_CONDA_SET_GEOMETRIC_DATA_DIR=%GEOMETRIC_DATA_DIR%"
)
@set "GEOMETRIC_DATA_DIR=%CONDA_PREFIX%\share\geometric_data"
