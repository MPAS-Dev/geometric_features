:: Restore previous GDAL env vars if they were set.

@set "GEOMETRIC_DATA_DIR="
@if defined _CONDA_SET_GEOMETRIC_DATA_DIR (
  set "GEOMETRIC_DATA_DIR=%_CONDA_SET_GEOMETRIC_DATA_DIR%"
  set "_CONDA_SET_GEOMETRIC_DATA_DIR="
)
