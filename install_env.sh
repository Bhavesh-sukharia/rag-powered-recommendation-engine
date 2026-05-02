#!/usr/bin/env bash
set -euo pipefail

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found. Please install Miniconda/Anaconda first."
  exit 1
fi

ENV_NAME=irs-env

echo "Creating conda environment '$ENV_NAME' from environment.yml..."
conda env create -f environment.yml || {
  echo "Environment creation failed. Try: conda env update -f environment.yml --prune"
  exit 1
}

echo "To activate: conda activate $ENV_NAME"
echo "Done."
