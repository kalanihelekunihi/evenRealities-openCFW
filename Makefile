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
        g2 g2-build g2-test g2-verify g2-inspect g2-clean \
        r1 r1-build r1-test r1-sanitize r1-verify r1-arm r1-sim r1-clean \
        third-party third-party-vendored third-party-fetched

all: build

help:
	@echo 'openCFW -- Even Realities G2 and R1 open firmware'
	@echo
	@echo 'Aggregate targets:'
	@echo '  build            build both targets (g2-build + r1-build)'
	@echo '  test             run both test suites (g2-test + r1-test)'
	@echo '  verify           full verification of both targets and all dependencies'
	@echo '  third-party      verify every vendored upstream snapshot'
	@echo '  clean            remove all build output from both targets'
	@echo
	@echo 'G2 (Apollo510 glasses firmware):'
	@echo '  g2-build         reference + ring-source + source profiles'
	@echo '  g2-test          G2 unit tests'
	@echo '  g2-verify        G2 build + upstream audits'
	@echo '  g2-inspect       inspect the built source package'
	@echo
	@echo 'R1 (nRF52840 ring firmware):'
	@echo '  r1-test          portable host tests'
	@echo '  r1-sanitize      host tests under ASan/UBSan'
	@echo '  r1-arm           freestanding Cortex-M4 objects'
	@echo '  r1-sim           host protocol/device simulator'
	@echo '  r1-verify        full R1 evidence gate (needs reconstructed images)'
	@echo
	@echo 'The R1 SDK image needs fetched vendor roots; see third-party/fetched/README.md.'
	@echo 'G2 targets need the official OTA blobs; see g2/blobs/official/*/PROVENANCE.md.'

# --- aggregates ------------------------------------------------------------

build: g2-build r1-build

test: g2-test r1-test

verify: g2-verify third-party r1-test

clean: g2-clean r1-clean

# --- G2 --------------------------------------------------------------------

g2: g2-build

g2-build:
	$(MAKE) -C $(G2_DIR) build

g2-test:
	$(MAKE) -C $(G2_DIR) test

g2-verify:
	$(MAKE) -C $(G2_DIR) verify

g2-inspect:
	$(MAKE) -C $(G2_DIR) inspect

g2-clean:
	$(MAKE) -C $(G2_DIR) clean

# --- R1 --------------------------------------------------------------------

r1: r1-build

# The portable reference implementation is what "building R1" means without a
# fetched Nordic SDK; the linked nRF52840 image is `make -C r1 sdk-image`.
r1-build: r1-arm r1-sim

r1-test:
	$(MAKE) -C $(R1_DIR) test

r1-sanitize:
	$(MAKE) -C $(R1_DIR) sanitize

# Needs the reconstructed R1 images; see
# r1/research/decompilation/rebuild/PROVENANCE.md.
r1-verify:
	$(MAKE) -C $(R1_DIR) verify

r1-arm:
	$(MAKE) -C $(R1_DIR) arm-objects

r1-sim:
	$(MAKE) -C $(R1_DIR) sim

r1-clean:
	$(MAKE) -C $(R1_DIR) clean

# --- third-party -----------------------------------------------------------

third-party: third-party-vendored

# Offline authentication of every vendored upstream snapshot. Consumed by both
# targets; see third-party/README.md for why the snapshots sit under g2/.
third-party-vendored:
	$(MAKE) -C $(G2_DIR) vendor-snapshots

# Requires the fetched vendor roots. Pass them through, for example:
#   make third-party-fetched SDK_ROOT=... FLASHDB_ROOT=... BMA456_ROOT=...
third-party-fetched:
	$(MAKE) -C $(R1_DIR) vendor-audit
