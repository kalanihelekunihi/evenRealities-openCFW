CC ?= cc
CLANG ?= clang
CPPFLAGS := -Iinclude -Ireconstructed -Iplatform/nrf52840
CFLAGS := -std=c11 -Wall -Wextra -Werror -Wpedantic -Wconversion -Wshadow -O2
SOURCES := src/r1_crc.c src/r1_protocol.c src/r1_health.c src/r1_health_db.c src/r1_twi_sync.c src/r1_retained_log.c src/r1_reset_trace.c src/r1_reset_reason.c src/r1_state.c src/r1_storage.c src/r1_kv_store.c src/r1_nv_recovery.c src/r1_sleep_db.c src/r1_persistence.c src/r1_connection_params.c src/r1_peer_target.c \
	src/r1_event.c src/r1_event_bus.c src/r1_dispatch.c src/r1_runtime.c src/r1_goodix.c src/r1_iqs7211e.c \
	src/r1_st25dvxxkc.c src/r1_power_lease.c src/r1_motion.c src/r1_wear.c src/r1_battery.c \
	src/r1_clock.c src/r1_gpio_registry.c port/goodix_gh3x2x/r1_gh3x2x_port.c \
	reconstructed/rtc_device/rtc_device.c \
	reconstructed/generic_device_registry/generic_device_registry.c \
	reconstructed/software_twi/software_twi.c \
	reconstructed/sensor_stream/sensor_stream.c \
	reconstructed/time_calendar/time_calendar.c \
	reconstructed/model_data/r1_model_data.c \
	reconstructed/quantized_runtime/quantized_runtime.c \
	reconstructed/gxt310/gxt310.c \
	reconstructed/qma6100/qma6100.c \
	reconstructed/yhm2710/yhm2710.c \
	reconstructed/goodix_primitives/goodix_primitives.c \
	reconstructed/goodix_heap/goodix_heap.c \
	reconstructed/gomore_primitives/gomore_primitives.c \
	reconstructed/gomore_tensor_runtime/gomore_tensor_runtime.c \
	platform/nrf52840/openr1_rtc_service.c
TEST_SOURCES := tests/test_openr1.c \
	tests/test_reconstructed_generic_device_registry.c \
	tests/test_reconstructed_software_twi.c \
	tests/test_reconstructed_sensor_stream.c \
	tests/test_reconstructed_time_calendar.c \
	tests/test_reconstructed_model_data.c \
	tests/test_reconstructed_quantized_runtime.c \
	tests/test_reconstructed_gxt310.c \
	tests/test_reconstructed_qma6100.c \
	tests/test_reconstructed_yhm2710.c \
	tests/test_reconstructed_goodix_primitives.c \
	tests/test_reconstructed_goodix_heap.c \
	tests/test_reconstructed_gomore_primitives.c \
	tests/test_reconstructed_gomore_tensor_runtime.c \
	tests/test_openr1_rtc_service.c
BUILD := build
HOST_TEST := $(BUILD)/test_openr1
SAN_TEST := $(BUILD)/test_openr1_sanitize
HOST_SIM := $(BUILD)/openr1_sim
ARM_BUILD := $(BUILD)/nrf52840
OWNER_SIGNING_DIR ?= config/r1-owner-signing
OWNER_DFU_OUTPUT ?= $(BUILD)/owner-dfu
OWNER_DFU_APPLICATION_VERSION ?= 3
OWNER_DFU_HARDWARE_VERSION ?= 52
OWNER_DFU_SD_REQ ?= 0x0100
WEST ?= west
ZEPHYR_WORKSPACE ?=
ZEPHYR_TOOLCHAIN ?=
ZEPHYR_BUILD ?= $(BUILD)/zephyr-sysbuild
ZEPHYR_BUNDLE ?= $(BUILD)/openr1-zephyr/openr1-source-built.zip
ZEPHYR_SIGNING_KEY ?=
ARM_FLAGS := --target=armv7em-none-eabi -mcpu=cortex-m4 -mthumb \
	-mfpu=fpv4-sp-d16 -mfloat-abi=hard -fno-math-errno \
	-std=c11 -ffreestanding -fno-builtin -fdata-sections -ffunction-sections \
	-Wall -Wextra -Werror -Wpedantic -Wconversion -Wshadow -Os -Iinclude -Ireconstructed -Iplatform/nrf52840
GOODIX_COMPOSER_SOURCE := port/goodix_gh3x2x/r1_gh3x2x_provider_composer.c
GOODIX_ROOT_SOURCE := port/goodix_gh3x2x/r1_gh3x2x_reconstructed_roots.c
ARM_SOURCES := $(SOURCES) $(GOODIX_COMPOSER_SOURCE) $(GOODIX_ROOT_SOURCE) \
	platform/nrf52840/r1_nrf52840.c
ARM_OBJECTS := $(patsubst %.c,$(ARM_BUILD)/%.o,$(ARM_SOURCES))

.PHONY: all test sim sanitize verify arm-objects provider-composer-check sdk-image sdk-verify bundle-boundary zephyr-source-verify zephyr-image zephyr-package zephyr-bundle zephyr-verify owner-dfu sdk-owner-dfu signing-test vendor-audit vendor-storage-test vendor-crypto-test vendor-goodix-test clean

all: test

$(HOST_TEST): $(SOURCES) $(TEST_SOURCES) | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SOURCES) $(TEST_SOURCES) -o $@

test: $(HOST_TEST)
	./$(HOST_TEST)

$(HOST_SIM): $(SOURCES) tools/openr1_sim.c | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SOURCES) tools/openr1_sim.c -o $@

sim: $(HOST_SIM)
	@echo "Built $(HOST_SIM)"

$(SAN_TEST): $(SOURCES) $(TEST_SOURCES) | $(BUILD)
	$(CLANG) $(CPPFLAGS) $(CFLAGS) -O1 -g -fno-omit-frame-pointer \
		-fsanitize=address,undefined $(SOURCES) $(TEST_SOURCES) -o $@

sanitize: $(SAN_TEST)
	ASAN_OPTIONS=detect_leaks=0 ./$(SAN_TEST)

arm-objects: $(ARM_OBJECTS)
	@echo "Built freestanding Cortex-M4 objects under $(ARM_BUILD)"

# Full evidence gate: capability ledger, source ownership, per-subsystem
# summaries, and the host/sanitizer/ARM builds. Needs the reconstructed
# images -- see research/decompilation/rebuild/PROVENANCE.md.
verify:
	python3 tools/verify_openr1.py

sdk-image:
	@test -n "$(SDK_ROOT)" || (echo "SDK_ROOT is required" >&2; exit 2)
	@test -n "$(BMA456_ROOT)" || (echo "BMA456_ROOT is required" >&2; exit 2)
	@test -n "$(LIS2DW12_ROOT)" || (echo "LIS2DW12_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(TINY_AES_ROOT)" || (echo "TINY_AES_ROOT is required" >&2; exit 2)
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	@test -n "$(GOODIX_DEMOCODE_ROOT)" || (echo "GOODIX_DEMOCODE_ROOT is required" >&2; exit 2)
	$(MAKE) -C platform/nrf52840/sdk SDK_ROOT="$(SDK_ROOT)" \
		BMA456_ROOT="$(BMA456_ROOT)" LIS2DW12_ROOT="$(LIS2DW12_ROOT)" \
		ST25DVXXKC_ROOT="$(ST25DVXXKC_ROOT)" \
		TINY_AES_ROOT="$(TINY_AES_ROOT)" \
		FLASHDB_ROOT="$(FLASHDB_ROOT)" \
		GOODIX_DEMOCODE_ROOT="$(GOODIX_DEMOCODE_ROOT)" \
		GNU_INSTALL_ROOT="$(GNU_INSTALL_ROOT)" default

sdk-verify: sdk-image
	python3 tools/verify_sdk_image.py

bundle-boundary:
	python3 tools/verify_application_bundle_boundary.py

zephyr-source-verify:
	python3 tools/verify_zephyr_source_boundary.py

zephyr-image:
	@test -n "$(ZEPHYR_WORKSPACE)" || (echo "ZEPHYR_WORKSPACE is required" >&2; exit 2)
	@test -n "$(ZEPHYR_TOOLCHAIN)" || (echo "ZEPHYR_TOOLCHAIN is required" >&2; exit 2)
	@test -n "$(BMA456_ROOT)" || (echo "BMA456_ROOT is required" >&2; exit 2)
	@test -n "$(LIS2DW12_ROOT)" || (echo "LIS2DW12_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	@test -n "$(GOODIX_DEMOCODE_ROOT)" || (echo "GOODIX_DEMOCODE_ROOT is required" >&2; exit 2)
	python3 tools/build_zephyr_bundle.py --workspace "$(ZEPHYR_WORKSPACE)" \
		--toolchain "$(ZEPHYR_TOOLCHAIN)" --west "$(WEST)" \
		--bma456-root "$(BMA456_ROOT)" --lis2dw12-root "$(LIS2DW12_ROOT)" \
		--st25dvxxkc-root "$(ST25DVXXKC_ROOT)" \
		--flashdb-root "$(FLASHDB_ROOT)" \
		--goodix-democode-root "$(GOODIX_DEMOCODE_ROOT)" \
		--build-dir "$(ZEPHYR_BUILD)" --build-only $(if $(ZEPHYR_SIGNING_KEY),--signing-key "$(ZEPHYR_SIGNING_KEY)")

zephyr-package:
	@test -n "$(ZEPHYR_WORKSPACE)" || (echo "ZEPHYR_WORKSPACE is required" >&2; exit 2)
	@test -n "$(BMA456_ROOT)" || (echo "BMA456_ROOT is required" >&2; exit 2)
	@test -n "$(LIS2DW12_ROOT)" || (echo "LIS2DW12_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	@test -n "$(GOODIX_DEMOCODE_ROOT)" || (echo "GOODIX_DEMOCODE_ROOT is required" >&2; exit 2)
	python3 tools/package_zephyr_bundle.py --build-dir "$(ZEPHYR_BUILD)" \
		--zephyr-workspace "$(ZEPHYR_WORKSPACE)" \
		--bma456-root "$(BMA456_ROOT)" --lis2dw12-root "$(LIS2DW12_ROOT)" \
		--st25dvxxkc-root "$(ST25DVXXKC_ROOT)" \
		--flashdb-root "$(FLASHDB_ROOT)" \
		--goodix-democode-root "$(GOODIX_DEMOCODE_ROOT)" \
		--output "$(ZEPHYR_BUNDLE)"

zephyr-bundle:
	@test -n "$(ZEPHYR_WORKSPACE)" || (echo "ZEPHYR_WORKSPACE is required" >&2; exit 2)
	@test -n "$(ZEPHYR_TOOLCHAIN)" || (echo "ZEPHYR_TOOLCHAIN is required" >&2; exit 2)
	@test -n "$(BMA456_ROOT)" || (echo "BMA456_ROOT is required" >&2; exit 2)
	@test -n "$(LIS2DW12_ROOT)" || (echo "LIS2DW12_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	@test -n "$(GOODIX_DEMOCODE_ROOT)" || (echo "GOODIX_DEMOCODE_ROOT is required" >&2; exit 2)
	python3 tools/build_zephyr_bundle.py --workspace "$(ZEPHYR_WORKSPACE)" \
		--toolchain "$(ZEPHYR_TOOLCHAIN)" --west "$(WEST)" \
		--bma456-root "$(BMA456_ROOT)" --lis2dw12-root "$(LIS2DW12_ROOT)" \
		--st25dvxxkc-root "$(ST25DVXXKC_ROOT)" \
		--flashdb-root "$(FLASHDB_ROOT)" \
		--goodix-democode-root "$(GOODIX_DEMOCODE_ROOT)" \
		--build-dir "$(ZEPHYR_BUILD)" --output "$(ZEPHYR_BUNDLE)" $(if $(ZEPHYR_SIGNING_KEY),--signing-key "$(ZEPHYR_SIGNING_KEY)")

zephyr-verify: zephyr-source-verify
	python3 tools/verify_zephyr_bundle.py "$(ZEPHYR_BUNDLE)"

# Package the linked OpenR1 application for the owner-keyed Nordic Secure DFU
# bootloader. The encrypted private key is local/ignored; its passphrase is
# loaded directly from macOS Keychain and is never placed in make variables.
owner-dfu:
	python3 tools/sign_r1_firmware.py \
		--source platform/nrf52840/sdk/_build/openr1_nrf52840_s140.bin \
		--key-directory "$(OWNER_SIGNING_DIR)" \
		--output "$(OWNER_DFU_OUTPUT)" \
		--application-version "$(OWNER_DFU_APPLICATION_VERSION)" \
		--hardware-version "$(OWNER_DFU_HARDWARE_VERSION)" \
		--sd-req "$(OWNER_DFU_SD_REQ)"

sdk-owner-dfu: sdk-image
	$(MAKE) owner-dfu

signing-test:
	python3 -m unittest discover -s tests -p 'test_sign_r1_firmware.py'

vendor-audit:
	@test -n "$(SDK_ROOT)" || (echo "SDK_ROOT is required" >&2; exit 2)
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	@test -n "$(BMA456_ROOT)" || (echo "BMA456_ROOT is required" >&2; exit 2)
	@test -n "$(LIS2DW12_ROOT)" || (echo "LIS2DW12_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(TINY_AES_ROOT)" || (echo "TINY_AES_ROOT is required" >&2; exit 2)
	@test -n "$(IQS7211E_ROOT)" || (echo "IQS7211E_ROOT is required" >&2; exit 2)
	@test -n "$(AZOTEQ_SETTINGS_ROOT)" || (echo "AZOTEQ_SETTINGS_ROOT is required" >&2; exit 2)
	python3 ../third-party/fetched/verify_vendor.py --sdk-root "$(SDK_ROOT)" \
		--flashdb-root "$(FLASHDB_ROOT)" --bma456-root "$(BMA456_ROOT)" \
		--lis2dw12-root "$(LIS2DW12_ROOT)" \
		--st25dvxxkc-root "$(ST25DVXXKC_ROOT)" \
		--tiny-aes-root "$(TINY_AES_ROOT)" \
		--iqs7211e-root "$(IQS7211E_ROOT)" \
		--azoteq-settings-root "$(AZOTEQ_SETTINGS_ROOT)" \
		$(if $(GOODIX_DEMOCODE_ROOT),--goodix-democode-root "$(GOODIX_DEMOCODE_ROOT)")

vendor-storage-test:
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	$(CC) $(CPPFLAGS) -Iport -I"$(FLASHDB_ROOT)/inc" \
		-I"$(FLASHDB_ROOT)/port/fal/inc" -std=c11 -O2 -Wall -Wextra \
		-Wno-unused-parameter -Wno-unused-but-set-variable \
		src/r1_storage.c port/r1_fal_port.c \
		"$(FLASHDB_ROOT)/src/fdb.c" "$(FLASHDB_ROOT)/src/fdb_tsdb.c" \
		"$(FLASHDB_ROOT)/src/fdb_utils.c" "$(FLASHDB_ROOT)/port/fal/src/fal.c" \
		"$(FLASHDB_ROOT)/port/fal/src/fal_flash.c" \
		"$(FLASHDB_ROOT)/port/fal/src/fal_partition.c" \
		tests/test_vendor_storage.c -o $(BUILD)/test_vendor_storage
	./$(BUILD)/test_vendor_storage

vendor-crypto-test: | $(BUILD)
	@test -n "$(TINY_AES_ROOT)" || (echo "TINY_AES_ROOT is required" >&2; exit 2)
	$(CC) $(CPPFLAGS) -I"$(TINY_AES_ROOT)" $(CFLAGS) -DECB=1 -DCBC=0 -DCTR=0 \
		-c src/r1_crypto.c -o $(BUILD)/r1_crypto.o
	$(CC) $(CPPFLAGS) -I"$(TINY_AES_ROOT)" $(CFLAGS) -DECB=1 -DCBC=0 -DCTR=0 \
		-c tests/test_vendor_crypto.c -o $(BUILD)/test_vendor_crypto.o
	$(CC) -I"$(TINY_AES_ROOT)" -std=c11 -O2 -Wall -Wextra -Wpedantic \
		-DECB=1 -DCBC=0 -DCTR=0 -c "$(TINY_AES_ROOT)/aes.c" \
		-o $(BUILD)/tiny_aes.o
	$(CC) $(BUILD)/r1_crypto.o $(BUILD)/test_vendor_crypto.o \
		$(BUILD)/tiny_aes.o -o $(BUILD)/test_vendor_crypto
	./$(BUILD)/test_vendor_crypto

# Goodix GH3X2X democode subset (pinned vendor tree; compiled with relaxed
# warnings like the other vendor components -- the strict project flags stay
# on the R1-authored port, which lives in SOURCES above).
GOODIX_DRIVER_DIR := $(GOODIX_DEMOCODE_ROOT)/demo_code/demo_kernel_code/driver
GOODIX_KERNEL_DIR := $(GOODIX_DEMOCODE_ROOT)/demo_code/demo_kernel_code/kernel
GOODIX_MODULE_DIR := $(GOODIX_DEMOCODE_ROOT)/demo_code/demo_kernel_code/module
GOODIX_ALGOAPP_INC := $(GOODIX_DEMOCODE_ROOT)/demo_code/demo_algo_code/goodix_algo_application/inc
GOODIX_ALGOCALL_INC := $(GOODIX_DEMOCODE_ROOT)/demo_code/demo_algo_code/goodix_algo_call/inc
GOODIX_SUBSET := \
	$(GOODIX_DRIVER_DIR)/src/gh_drv_config.c \
	$(GOODIX_DRIVER_DIR)/src/gh_drv_control.c \
	$(GOODIX_DRIVER_DIR)/src/gh_drv_dump.c \
	$(GOODIX_DRIVER_DIR)/src/gh_drv_interface.c \
	$(GOODIX_KERNEL_DIR)/gh_demo.c \
	$(GOODIX_KERNEL_DIR)/gh_demo_hook.c \
	$(GOODIX_KERNEL_DIR)/gh_demo_reg_array.c \
	$(GOODIX_KERNEL_DIR)/gh_demo_user.c \
	$(GOODIX_MODULE_DIR)/gh_agc/gh_agc.c \
	$(GOODIX_MODULE_DIR)/gh_other/gh_changeinttime.c \
	$(GOODIX_MODULE_DIR)/gh_other/gh_movedetect.c \
	$(GOODIX_MODULE_DIR)/gh_soft_adt/gh_multi_sen_pro.c \
	$(GOODIX_DEMOCODE_ROOT)/algo_lib/algo_params/HR/04_EXCLUSIVE/goodix_hba_config.c \
	$(GOODIX_DEMOCODE_ROOT)/algo_lib/algo_params/goodix_hrv_config.c \
	$(GOODIX_DEMOCODE_ROOT)/algo_lib/algo_params/SPO2/goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c
GOODIX_INCLUDES := \
	-Iport/goodix_gh3x2x/config \
	-I$(GOODIX_DRIVER_DIR)/inc \
	-I$(GOODIX_KERNEL_DIR) \
	-I$(GOODIX_MODULE_DIR)/gh_agc \
	-I$(GOODIX_MODULE_DIR)/gh_ecg \
	-I$(GOODIX_MODULE_DIR)/gh_other \
	-I$(GOODIX_MODULE_DIR)/gh_protocol \
	-I$(GOODIX_MODULE_DIR)/gh_soft_adt \
	-I$(GOODIX_ALGOAPP_INC) \
	-I$(GOODIX_ALGOCALL_INC) \
	-I$(GOODIX_ALGOCALL_INC)/hr_exc \
	-I$(GOODIX_ALGOCALL_INC)/spo2_pre_exc
GOODIX_PORT_SOURCES := \
	port/goodix_gh3x2x/r1_gh3x2x_port.c \
	port/goodix_gh3x2x/r1_gh3x2x_bind.c \
	port/goodix_gh3x2x/r1_gh3x2x_provider_composer.c \
	port/goodix_gh3x2x/r1_gh3x2x_reconstructed_roots.c \
	port/goodix_gh3x2x/r1_gh3x2x_stubs.c
GOODIX_RECONSTRUCTED_SOURCES := \
	reconstructed/model_data/r1_model_data.c \
	reconstructed/quantized_runtime/quantized_runtime.c \
	reconstructed/goodix_primitives/goodix_primitives.c

provider-composer-check: | $(BUILD)
	$(CC) $(CPPFLAGS) -Iport/goodix_gh3x2x $(CFLAGS) -c \
		$(GOODIX_COMPOSER_SOURCE) -o $(BUILD)/r1_gh3x2x_provider_composer.strict.o
	$(CC) $(CPPFLAGS) -Iport/goodix_gh3x2x $(CFLAGS) -c \
		$(GOODIX_ROOT_SOURCE) -o $(BUILD)/r1_gh3x2x_reconstructed_roots.strict.o

vendor-goodix-test: provider-composer-check | $(BUILD)
	@test -n "$(GOODIX_DEMOCODE_ROOT)" || (echo "GOODIX_DEMOCODE_ROOT is required" >&2; exit 2)
	$(CC) $(CPPFLAGS) -Iport/goodix_gh3x2x $(GOODIX_INCLUDES) \
		-std=c11 -O2 -Wall -Wextra -Wno-unused-parameter \
		src/r1_goodix.c $(GOODIX_SUBSET) $(GOODIX_RECONSTRUCTED_SOURCES) \
		$(GOODIX_PORT_SOURCES) \
		tests/test_vendor_goodix.c -lm -o $(BUILD)/test_vendor_goodix
	./$(BUILD)/test_vendor_goodix

$(ARM_BUILD)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CLANG) $(ARM_FLAGS) -c $< -o $@

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
