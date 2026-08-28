#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

OPENCFW_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec make -C "$OPENCFW_ROOT" "$@"
