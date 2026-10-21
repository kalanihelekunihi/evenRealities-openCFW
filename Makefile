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
        build open-build test verify clean sources sources-check sources-qualify \
        g2 g2-build g2-test g2-verify g2-clean \
        r1 r1-test r1-verify r1-clean \
        third-party third-party-submodules third-party-fetched tools \
        cut-verify blockers

all: build

help:
	@echo 'openCFW -- Even Realities G2 and R1 open firmware'
	@echo
	@echo 'Aggregate targets:'
	@echo '  build            default license-free Clang/GNU hybrid build'
	@echo '  open-build       explicit alias for the default build'
	@echo '  test             run both test suites (g2-test + r1-test)'
	@echo '  verify           reference/oracle verification of both targets'
	@echo '  third-party      check initialised submodules are at their pinned commits'
	@echo '  clean            remove all build output from both targets'
	@echo
	@echo 'Reconstructed source (g2/src, r1/src):'
	@echo '  sources          compile every unit in g2/src/sources.json and r1/src/sources.json'
	@echo '  sources-check    every source file is listed once and every unit exists (no compiler)'
	@echo '  sources-qualify  compare compiled anchored functions with the stock payloads'
	@echo
	@echo 'G2 (Apollo510 glasses firmware):'
	@echo '  g2-build         compile selected G2 source and build hybrid EVENOTA'
	@echo '  g2-reference     repack the official G2 payloads as a reference'
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
	@echo '  cut-verify       reassemble every payload from its region manifest, byte-identically'
	@echo '  blockers         retained bytes per payload and per MISSING-TOOLCHAIN.md blocker'
	@echo '  hybrid-build     build G2 OTA + R1 application with exclusive region provenance'
	@echo '  g2-hybrid-build  hybrid G2 OTA; HYBRID_OUT must be a fresh directory'
	@echo '  r1-build         hybrid R1 application OTA; HYBRID_OUT must be fresh'
	@echo '  hybrid-test      hybrid source/resource accounting checks'
	@echo '  coverage         show strict coverage percentages for HYBRID_OUT'

# --- aggregates ------------------------------------------------------------

build: open-build

open-build: hybrid-build

test: sources-check g2-test r1-test hybrid-test
	$(PYTHON) -m unittest tools/cutting/test_firmware_cut.py

verify: g2-verify r1-verify

clean: g2-clean r1-clean

# --- reconstructed source --------------------------------------------------

SOURCES_OUT ?= build/sources
QUALIFY_OUT ?= build/qualify

sources:
	$(PYTHON) tools/build/sources.py build --out "$(SOURCES_OUT)"

sources-check:
	$(PYTHON) tools/build/sources.py check

sources-qualify:
	$(PYTHON) tools/build/qualify_sources.py --out "$(QUALIFY_OUT)"

# --- G2 --------------------------------------------------------------------

g2: g2-build

g2-build: g2-hybrid-build

g2-reference:
	$(MAKE) -C $(G2_DIR) reference

g2-test:
	$(MAKE) -C $(G2_DIR) core-test

g2-verify:
	$(MAKE) -C $(G2_DIR) reference-verify

g2-clean:
	$(MAKE) -C $(G2_DIR) clean

# --- R1 --------------------------------------------------------------------

r1: r1-build

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

# --- firmware cutting (MISSING-TOOLCHAIN.md) -------------------------------

cut-verify:
	$(PYTHON) tools/cutting/firmware_cut.py verify
	$(PYTHON) -m unittest tools/cutting/test_firmware_cut.py

blockers:
	$(PYTHON) tools/cutting/firmware_cut.py report

# Explicit hybrid assembly; retained executable bytes never imply source completeness.
HYBRID_OUT ?= build/hybrid
.PHONY: hybrid-build g2-hybrid-build r1-build hybrid-test g2-reference
hybrid-build:
	$(PYTHON) tools/build/build_firmware.py --out "$(HYBRID_OUT)"
g2-hybrid-build:
	$(PYTHON) tools/build/build_firmware.py --device g2 --out "$(HYBRID_OUT)"
r1-build:
	$(PYTHON) tools/build/build_firmware.py --device r1 --out "$(HYBRID_OUT)"
hybrid-test:
	$(PYTHON) -m unittest discover -s tools/build -p 'test_*.py'

.PHONY: coverage
coverage:
	$(PYTHON) tools/build/report_coverage.py "$(HYBRID_OUT)/coverage.json"
