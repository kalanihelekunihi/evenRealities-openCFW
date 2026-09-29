# SPDX-License-Identifier: MIT
# R1 ring (nRF52840): decompilation corpus, rebuild oracle and vendor audit.
#
# The stock firmware is nRF5 SDK 17.1.0 + S140 7.2.0 + FreeRTOS 10.5.1, built
# with Arm Compiler 5.  See docs/toolchain-and-dependencies.md.  Official images
# go under blobs/official/2.2.6.0009/ (see its PROVENANCE.md); they are never
# tracked.

PYTHON ?= python3
REBUILD_DIR := research/decompilation/rebuild

.PHONY: all test verify oracle vendor-audit bootloader-decompilation \
        bootloader-source-correlation application-source-correlation clean

all: test

# Structural checks on the tracked decompilation corpus.  No vendor bytes needed.
test:
	$(PYTHON) tools/verify_r1_decompilation.py --corpus-only

# Full check: corpus plus the exact-byte image oracle.  Needs the *.bytes.inc
# arrays generated from your own official images.
verify:
	$(PYTHON) tools/verify_r1_decompilation.py

oracle:
	$(MAKE) -C $(REBUILD_DIR) verify

# Authenticate the fetched vendor archives (nRF5 SDK, sensor APIs, ...) and the
# FreeRTOS / CMSIS-FreeRTOS / CmBacktrace submodules.  Pass the unpacked roots,
# for example after `third-party/fetched/fetch.sh /abs/cache`.
vendor-audit:
	@test -n "$(SDK_ROOT)" || (echo "SDK_ROOT is required" >&2; exit 2)
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	@test -n "$(BMA456_ROOT)" || (echo "BMA456_ROOT is required" >&2; exit 2)
	@test -n "$(LIS2DW12_ROOT)" || (echo "LIS2DW12_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(TINY_AES_ROOT)" || (echo "TINY_AES_ROOT is required" >&2; exit 2)
	@test -n "$(IQS7211E_ROOT)" || (echo "IQS7211E_ROOT is required" >&2; exit 2)
	@test -n "$(AZOTEQ_SETTINGS_ROOT)" || (echo "AZOTEQ_SETTINGS_ROOT is required" >&2; exit 2)
	$(PYTHON) ../third-party/fetched/verify_vendor.py --sdk-root "$(SDK_ROOT)" \
		--flashdb-root "$(FLASHDB_ROOT)" --bma456-root "$(BMA456_ROOT)" \
		--lis2dw12-root "$(LIS2DW12_ROOT)" \
		--st25dvxxkc-root "$(ST25DVXXKC_ROOT)" \
		--tiny-aes-root "$(TINY_AES_ROOT)" \
		--iqs7211e-root "$(IQS7211E_ROOT)" \
		--azoteq-settings-root "$(AZOTEQ_SETTINGS_ROOT)" \
		$(if $(GOODIX_DEMOCODE_ROOT),--goodix-democode-root "$(GOODIX_DEMOCODE_ROOT)")

# Headless Ghidra runs; need GHIDRA_INSTALL_DIR (or R1_GHIDRA_HEADLESS) and a
# Java 21 home in R1_JAVA_RUNTIME, plus the official images.
bootloader-decompilation:
	sh tools/run_r1_bootloader_decompilation.sh

bootloader-source-correlation:
	sh tools/run_r1_bootloader_source_correlation.sh

application-source-correlation:
	sh tools/run_r1_application_source_correlation.sh

clean:
	$(MAKE) -C $(REBUILD_DIR) clean
