CC ?= cc
CLANG ?= clang
CPPFLAGS := -Iinclude
CFLAGS := -std=c11 -Wall -Wextra -Werror -Wpedantic -Wconversion -Wshadow -O2
SOURCES := src/r1_crc.c src/r1_protocol.c src/r1_health.c src/r1_health_db.c src/r1_twi_sync.c src/r1_retained_log.c src/r1_reset_trace.c src/r1_reset_reason.c src/r1_state.c src/r1_storage.c src/r1_kv_store.c src/r1_nv_recovery.c src/r1_sleep_db.c src/r1_persistence.c src/r1_connection_params.c src/r1_peer_target.c \
	src/r1_event.c src/r1_event_bus.c src/r1_dispatch.c src/r1_runtime.c src/r1_goodix.c src/r1_iqs7211e.c \
	src/r1_st25dvxxkc.c src/r1_power_lease.c src/r1_motion.c src/r1_wear.c src/r1_battery.c \
	src/r1_clock.c port/goodix_gh3x2x/r1_gh3x2x_port.c
TEST_SOURCES := tests/test_openr1.c
BUILD := build
HOST_TEST := $(BUILD)/test_openr1
SAN_TEST := $(BUILD)/test_openr1_sanitize
HOST_SIM := $(BUILD)/openr1_sim
ARM_BUILD := $(BUILD)/nrf52840
ARM_FLAGS := --target=armv7em-none-eabi -mcpu=cortex-m4 -mthumb \
	-mfpu=fpv4-sp-d16 -mfloat-abi=hard -fno-math-errno \
	-std=c11 -ffreestanding -fno-builtin -fdata-sections -ffunction-sections \
	-Wall -Wextra -Werror -Wpedantic -Wconversion -Wshadow -Os -Iinclude
ARM_SOURCES := $(SOURCES) platform/nrf52840/r1_nrf52840.c
ARM_OBJECTS := $(patsubst %.c,$(ARM_BUILD)/%.o,$(ARM_SOURCES))

.PHONY: all test sim sanitize verify arm-objects sdk-image sdk-verify vendor-audit vendor-storage-test vendor-crypto-test vendor-goodix-test clean

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
	port/goodix_gh3x2x/r1_gh3x2x_stubs.c

vendor-goodix-test: | $(BUILD)
	@test -n "$(GOODIX_DEMOCODE_ROOT)" || (echo "GOODIX_DEMOCODE_ROOT is required" >&2; exit 2)
	$(CC) $(CPPFLAGS) -Iport/goodix_gh3x2x $(GOODIX_INCLUDES) \
		-std=c11 -O2 -Wall -Wextra -Wno-unused-parameter \
		src/r1_goodix.c $(GOODIX_SUBSET) $(GOODIX_PORT_SOURCES) \
		tests/test_vendor_goodix.c -lm -o $(BUILD)/test_vendor_goodix
	./$(BUILD)/test_vendor_goodix

$(ARM_BUILD)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CLANG) $(ARM_FLAGS) -c $< -o $@

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
