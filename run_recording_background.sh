#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <project_dir>"
  exit 1
fi

PROJECT_DIR="$1"

cd "$PROJECT_DIR" || exit 1

source "$PROJECT_DIR/.venv/bin/activate"

python3 "$PROJECT_DIR/cab.py" --env --remove_silence
