#!/usr/bin/env bash

echo $with_data

$PYTHON -m pip install . --no-deps -vv

if [ "$with_data" == "True" ]; then
  cp -r "${SRC_DIR}/geometric_data" "${PREFIX}/share/geometric_data"

  ACTIVATE_DIR="${PREFIX}/etc/conda/activate.d"
  DEACTIVATE_DIR="${PREFIX}/etc/conda/deactivate.d"
  mkdir -p "${ACTIVATE_DIR}"
  mkdir -p "${DEACTIVATE_DIR}"

  cp "${RECIPE_DIR}/scripts/activate.sh" "${ACTIVATE_DIR}/geometric_features-activate.sh"
  cp "${RECIPE_DIR}/scripts/deactivate.sh" "${DEACTIVATE_DIR}/geometric_features-deactivate.sh"
  cp "${RECIPE_DIR}/scripts/activate.csh" "${ACTIVATE_DIR}/geometric_features-activate.csh"
  cp "${RECIPE_DIR}/scripts/deactivate.csh" "${DEACTIVATE_DIR}/geometric_features-deactivate.csh"
  cp "${RECIPE_DIR}/scripts/activate.fish" "${ACTIVATE_DIR}/geometric_features-activate.fish"
  cp "${RECIPE_DIR}/scripts/deactivate.fish" "${DEACTIVATE_DIR}/geometric_features-deactivate.fish"
  cp "${RECIPE_DIR}/scripts/activate.bat" "${ACTIVATE_DIR}/geometric_features-activate.bat"
  cp "${RECIPE_DIR}/scripts/deactivate.bat" "${DEACTIVATE_DIR}/geometric_features-deactivate.bat"
fi
