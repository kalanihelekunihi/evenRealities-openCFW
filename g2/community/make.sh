#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

OPENCFW_COMMUNITY_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec make -C "$OPENCFW_COMMUNITY_ROOT" "$@"
