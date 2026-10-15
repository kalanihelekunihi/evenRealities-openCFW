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

# Compile recovered provider candidates for ARM; does not link a stock image.
.PHONY: source-candidates
source-candidates:
	$(PYTHON) tools/build_source_candidates.py


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

.PHONY: checksum-oracle
checksum-oracle:
	$(PYTHON) tools/verify_stock_checksums.py

.PHONY: public-providers
public-providers:
	$(PYTHON) tools/build_public_providers.py

.PHONY: rtos-candidate static-memory-oracle
rtos-candidate:
	$(PYTHON) tools/build_rtos_candidate.py

static-memory-oracle:
	$(PYTHON) tools/verify_static_task_memory.py

.PHONY: crypto-candidate crypto-oracle source-frontier
crypto-candidate:
	$(PYTHON) tools/build_crypto_candidate.py

crypto-oracle:
	$(PYTHON) tools/verify_two_pass_crypto.py

source-frontier:
	$(PYTHON) tools/audit_source_frontier.py

.PHONY: application-sdk
application-sdk:
	$(PYTHON) tools/build_application_sdk.py

.PHONY: goodix-candidate goodix-config-oracle
goodix-candidate:
	$(PYTHON) tools/build_goodix_candidate.py

goodix-config-oracle:
	$(PYTHON) tools/verify_goodix_configuration.py

.PHONY: sensor-candidates st25-bus-oracle
sensor-candidates:
	$(PYTHON) tools/build_sensor_candidates.py

st25-bus-oracle:
	$(PYTHON) tools/verify_st25_bus_bindings.py

.PHONY: i2c5-candidate i2c5-oracle
i2c5-candidate:
	$(PYTHON) tools/build_i2c5_candidate.py

i2c5-oracle:
	$(PYTHON) tools/verify_i2c5_integration.py
	$(PYTHON) tools/verify_registry_bootstrap.py
	$(PYTHON) tools/verify_registry_dispatch.py
	$(PYTHON) tools/verify_twi_lifecycle.py
	$(PYTHON) tools/verify_twi_adapters.py
	$(PYTHON) tools/verify_twi_adapters.py --null-buffers
	$(PYTHON) tools/verify_twi_native_initialization.py

.PHONY: software-twi-oracle
software-twi-oracle:
	$(PYTHON) tools/verify_software_twi_primitives.py
	$(PYTHON) tools/verify_software_twi_primitives.py --transactions
	$(PYTHON) tools/verify_twi_board_configuration.py

.PHONY: twi-gpio-candidate twi-gpio-oracle
twi-gpio-candidate:
	$(PYTHON) tools/build_twi_gpio.py
twi-gpio-oracle:
	$(PYTHON) tools/verify_twi_gpio.py
	$(PYTHON) tools/verify_twi_delays.py

.PHONY: named-gpio-candidate named-gpio-oracle
named-gpio-candidate:
	$(PYTHON) tools/build_named_gpio.py
named-gpio-oracle:
	$(PYTHON) tools/verify_named_gpio.py
	$(PYTHON) tools/verify_gpio_sdk_execution.py

.PHONY: named-adc-candidate named-adc-oracle
named-adc-candidate:
	$(PYTHON) tools/build_named_adc.py
named-adc-oracle:
	$(PYTHON) tools/verify_named_adc.py
	$(PYTHON) tools/verify_adc_sdk_execution.py

.PHONY: native-board-candidate native-board-oracle
native-board-candidate:
	$(PYTHON) tools/build_native_board.py
native-board-oracle:
	$(PYTHON) tools/verify_native_board.py

.PHONY: memory-runtime-candidate memory-runtime-oracle
memory-runtime-candidate:
	$(PYTHON) tools/build_memory_runtime.py
memory-runtime-oracle:
	$(PYTHON) tools/verify_memory_runtime.py

.PHONY: board-seams-candidate board-seams-oracle
board-seams-candidate:
	$(PYTHON) tools/build_board_seams.py
board-seams-oracle:
	$(PYTHON) tools/verify_board_seams.py

.PHONY: structured-log-candidate structured-log-oracle
structured-log-candidate:
	$(PYTHON) tools/build_structured_log.py
structured-log-oracle:
	$(PYTHON) tools/verify_structured_log.py
	$(PYTHON) tools/verify_structured_log.py --real-critical

.PHONY: rtos-critical-candidate rtos-critical-oracle
rtos-critical-candidate:
	$(PYTHON) tools/build_rtos_critical.py
rtos-critical-oracle:
	$(PYTHON) tools/verify_rtos_critical.py

.PHONY: structured-encode-candidate structured-encode-oracle
structured-encode-candidate:
	$(PYTHON) tools/build_structured_encode.py
structured-encode-oracle:
	$(PYTHON) tools/verify_structured_encode.py
	$(PYTHON) tools/verify_structured_encode.py --real-float

.PHONY: structured-time-candidate structured-time-oracle
structured-time-candidate:
	$(PYTHON) tools/build_structured_time.py
structured-time-oracle:
	$(PYTHON) tools/verify_structured_time.py

.PHONY: rtos-ticks-candidate rtos-ticks-oracle structured-float-candidate structured-float-oracle structured-cache-candidate structured-cache-oracle
rtos-ticks-candidate:
	$(PYTHON) tools/build_rtos_ticks.py
rtos-ticks-oracle:
	$(PYTHON) tools/verify_rtos_ticks.py
structured-float-candidate:
	$(PYTHON) tools/build_structured_float.py
structured-float-oracle:
	$(PYTHON) tools/verify_structured_float.py
structured-cache-candidate:
	$(PYTHON) tools/build_structured_cache.py
	$(PYTHON) tools/build_structured_cache_copy.py
structured-cache-oracle:
	$(PYTHON) tools/verify_structured_cache.py
	$(PYTHON) tools/verify_structured_cache_copy.py
	$(PYTHON) tools/verify_structured_cache.py --real-copy

.PHONY: native-events-candidate native-events-oracle connection-handle-candidate connection-handle-oracle
native-events-candidate:
	$(PYTHON) tools/build_native_events.py
native-events-oracle:
	$(PYTHON) tools/verify_native_events.py
connection-handle-candidate:
	$(PYTHON) tools/build_connection_handle.py
connection-handle-oracle:
	$(PYTHON) tools/verify_connection_handle.py

.PHONY: native-tx-candidate native-tx-oracle native-task-lifecycle-candidate native-task-lifecycle-oracle
native-tx-candidate:
	$(PYTHON) tools/build_native_tx.py
native-tx-oracle:
	$(PYTHON) tools/verify_native_tx.py
native-task-lifecycle-candidate:
	$(PYTHON) tools/build_native_task_lifecycle.py
native-task-lifecycle-oracle:
	$(PYTHON) tools/verify_native_task_lifecycle.py

.PHONY: native-tasks-candidate native-tasks-oracle native-sync-candidate native-sync-oracle
native-tasks-candidate:
	$(PYTHON) tools/build_native_tasks.py
native-tasks-oracle:
	$(PYTHON) tools/verify_native_tasks.py
	$(PYTHON) tools/verify_native_tasks.py --real-sync
	$(PYTHON) tools/verify_native_tasks.py --real-watchdog
native-sync-candidate:
	$(PYTHON) tools/build_native_sync.py
native-sync-oracle:
	$(PYTHON) tools/verify_native_sync.py

.PHONY: native-watchdog-candidate native-watchdog-oracle native-event-dispatch-candidate native-event-dispatch-oracle
native-watchdog-candidate:
	$(PYTHON) tools/build_native_watchdog.py
native-watchdog-oracle:
	$(PYTHON) tools/verify_native_watchdog.py
native-event-dispatch-candidate:
	$(PYTHON) tools/build_native_event_dispatch.py
native-event-dispatch-oracle:
	$(PYTHON) tools/verify_native_event_dispatch.py

.PHONY: watchdog-startup-candidate watchdog-startup-oracle
watchdog-startup-candidate:
	$(PYTHON) tools/build_watchdog_startup.py
watchdog-startup-oracle:
	$(PYTHON) tools/verify_watchdog_manager.py
	$(PYTHON) tools/verify_watchdog_device.py
	$(PYTHON) tools/verify_watchdog_device.py --sdk
