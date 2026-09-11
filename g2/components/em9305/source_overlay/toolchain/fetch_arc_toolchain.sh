#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Installs the pinned, reproducible macOS-native ARCv2 (EM9305) GCC/binutils
# cross toolchain used by ../build_overlay.py.  See TOOLCHAIN.md for the
# full pin record and rationale (this replaces the earlier, undocumented
# `opencfw-arc-toolchain:fedora44` Docker image, which has no build recipe
# in this repository and is not present on this host).
#
# Usage: components/em9305/source_overlay/toolchain/fetch_arc_toolchain.sh
#
# Downloads the Zephyr SDK v1.0.1 "arc-zephyr-elf" GNU toolchain release
# asset for macOS/aarch64, verifies its SHA-256 against the pin below (which
# matches the upstream sdk-ng v1.0.1 sha256.sum release manifest), and
# extracts it to $OPENCFW_ARC_TOOLCHAIN_DIR (default:
# ~/.cache/opencfw/toolchains/arc-zephyr-elf-1.0.1).  build_overlay.py picks
# up a toolchain installed at that default location automatically; no
# environment variables are required after running this script.
#
# Only macOS/arm64 hosts are pinned today (this is the only macOS host this
# item had available).  Re-run with OPENCFW_ARC_ASSET/OPENCFW_ARC_SHA256 set
# to add an Intel-mac pin once someone has verified one; see TOOLCHAIN.md.

set -euo pipefail

RELEASE_TAG="v1.0.1"
ASSET_DEFAULT="toolchain_gnu_macos-aarch64_arc-zephyr-elf.tar.xz"
SHA256_DEFAULT="b3fbd56e8920a9a65230ed34de1d4af47bbb2411a6e45c4ae25f1830be039f1f"

ASSET="${OPENCFW_ARC_ASSET:-$ASSET_DEFAULT}"
EXPECTED_SHA256="${OPENCFW_ARC_SHA256:-$SHA256_DEFAULT}"
URL="https://github.com/zephyrproject-rtos/sdk-ng/releases/download/${RELEASE_TAG}/${ASSET}"

DEST_DIR="${OPENCFW_ARC_TOOLCHAIN_DIR:-$HOME/.cache/opencfw/toolchains/arc-zephyr-elf-1.0.1}"

if [ -x "$DEST_DIR/bin/arc-zephyr-elf-gcc" ]; then
  echo "fetch_arc_toolchain: already installed at $DEST_DIR" >&2
  exit 0
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ARCHIVE="$WORK/$ASSET"
echo "fetch_arc_toolchain: downloading $URL" >&2
curl -fL --retry 3 -o "$ARCHIVE" "$URL"

ACTUAL_SHA256="$(shasum -a 256 "$ARCHIVE" | awk '{print $1}')"
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
  echo "fetch_arc_toolchain: SHA-256 mismatch for $ASSET" >&2
  echo "  expected: $EXPECTED_SHA256" >&2
  echo "  actual:   $ACTUAL_SHA256" >&2
  exit 1
fi

mkdir -p "$(dirname "$DEST_DIR")"
EXTRACT="$WORK/extract"
mkdir -p "$EXTRACT"
tar -xJf "$ARCHIVE" -C "$EXTRACT"

# The archive's top-level directory is the bare triple ("arc-zephyr-elf");
# rename it to the version-qualified destination so multiple pinned
# releases can coexist under the cache root.
SRC_DIR="$EXTRACT/arc-zephyr-elf"
if [ ! -d "$SRC_DIR" ]; then
  echo "fetch_arc_toolchain: unexpected archive layout, no arc-zephyr-elf/ directory" >&2
  exit 1
fi
rm -rf "$DEST_DIR"
mv "$SRC_DIR" "$DEST_DIR"

"$DEST_DIR/bin/arc-zephyr-elf-gcc" --version | head -1
echo "fetch_arc_toolchain: installed to $DEST_DIR" >&2
