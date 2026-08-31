#!/bin/sh
# SPDX-License-Identifier: MIT
# Run the unified openCFW build from anywhere:  ./make.sh [target...]
set -eu

OPENCFW_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec make -C "$OPENCFW_ROOT" "$@"
