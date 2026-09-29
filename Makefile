# SPDX-License-Identifier: MIT
# openCFW -- unified entry point for the G2 and R1 firmware targets.
#
# Each target keeps its own build system; this Makefile is the front door that
# dispatches to them and provides the cross-target aggregates. Anything not
# listed here can still be run directly, for example:
#
#     make -C g2 lvgl-snapshot
#     make -C r1 sanitize
#
# Every target below fails closed. A hash, checksum, region, or provenance
# mismatch aborts the build instead of degrading to a warning.

MAKE ?= make
PYTHON ?= python3

G2_DIR := g2
R1_DIR := r1
THIRD_PARTY_DIR := third-party

.PHONY: all help \
        build test verify clean \
        g2 g2-build g2-test g2-verify g2-clean \
        r1 r1-test r1-verify r1-clean \
        third-party third-party-submodules third-party-fetched tools

all: build

help:
	@echo 'openCFW -- Even Realities G2 and R1 open firmware'
	@echo
	@echo 'Aggregate targets:'
	@echo '  build            G2 reference repack (the R1 rebuild oracle is r1-verify)'
	@echo '  test             run both test suites (g2-test + r1-test)'
	@echo '  verify           reference/oracle verification of both targets'
	@echo '  third-party      check initialised submodules are at their pinned commits'
	@echo '  clean            remove all build output from both targets'
	@echo
	@echo 'G2 (Apollo510 glasses firmware):'
	@echo '  g2-build         byte-identical reference EVENOTA from the official payloads'
	@echo '  g2-test          tests for the kept G2 format, analyzer and Ghidra tools'
	@echo '  g2-verify        reference build + manifest and research-corpus verification'
	@echo
	@echo 'R1 (nRF52840 ring firmware):'
	@echo '  r1-test          structural check of the tracked decompilation corpus'
	@echo '  r1-verify        corpus + exact-byte image oracle (needs official images)'
	@echo
	@echo 'R1 vendor archives: third-party/fetched/README.md; images: r1/blobs/official/*/PROVENANCE.md.'
	@echo 'G2 targets need the official OTA blobs; see g2/blobs/official/*/PROVENANCE.md.'
	@echo
	@echo 'Tooling:'
	@echo '  tools            list the pinned analysis tools (tools/bootstrap)'

# --- aggregates ------------------------------------------------------------

build: g2-build

test: g2-test r1-test

verify: g2-verify r1-verify

clean: g2-clean r1-clean

# --- G2 --------------------------------------------------------------------

g2: g2-build

g2-build:
	$(MAKE) -C $(G2_DIR) reference

g2-test:
	$(MAKE) -C $(G2_DIR) core-test

g2-verify:
	$(MAKE) -C $(G2_DIR) reference-verify

g2-clean:
	$(MAKE) -C $(G2_DIR) clean

# --- R1 --------------------------------------------------------------------

r1: r1-test

r1-test:
	$(MAKE) -C $(R1_DIR) test

r1-verify:
	$(MAKE) -C $(R1_DIR) verify

r1-clean:
	$(MAKE) -C $(R1_DIR) clean

# --- third-party -----------------------------------------------------------

third-party: third-party-submodules

# Fails if any initialised submodule is checked out away from its pinned
# commit or has conflicts.  Uninitialised submodules are fine.
third-party-submodules:
	@git submodule status | awk '/^[+U]/ {bad=1; print "not at pinned commit: " $$2} END {exit bad}'
	@echo "third-party: every initialised submodule is at its pinned commit"

# Authenticates the fetched R1 archives; pass the unpacked roots, for example:
#   make third-party-fetched SDK_ROOT=... FLASHDB_ROOT=... BMA456_ROOT=...
third-party-fetched:
	$(MAKE) -C $(R1_DIR) vendor-audit

# --- tooling ---------------------------------------------------------------

# Pinned analysis tools; see docs/tooling.md. Install with
#   tools/bootstrap/bootstrap.py --prefix /absolute/path
tools:
	$(PYTHON) tools/bootstrap/bootstrap.py --list
