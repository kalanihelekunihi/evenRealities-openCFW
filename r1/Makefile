CC ?= cc
CLANG ?= clang
CPPFLAGS := -Iinclude
CFLAGS := -std=c11 -Wall -Wextra -Werror -Wpedantic -Wconversion -Wshadow -O2
SOURCES := src/r1_crc.c src/r1_protocol.c src/r1_health.c src/r1_health_db.c src/r1_twi_sync.c src/r1_retained_log.c src/r1_reset_trace.c src/r1_reset_reason.c src/r1_state.c src/r1_storage.c src/r1_kv_store.c src/r1_nv_recovery.c src/r1_sleep_db.c src/r1_persistence.c src/r1_connection_params.c src/r1_peer_target.c \
	src/r1_event.c src/r1_dispatch.c src/r1_runtime.c src/r1_goodix.c src/r1_iqs7211e.c \
	src/r1_st25dvxxkc.c src/r1_power_lease.c src/r1_motion.c src/r1_wear.c src/r1_battery.c
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

.PHONY: all test sim sanitize arm-objects sdk-image sdk-verify vendor-audit vendor-storage-test vendor-crypto-test clean

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

sdk-image:
	@test -n "$(SDK_ROOT)" || (echo "SDK_ROOT is required" >&2; exit 2)
	@test -n "$(BMA456_ROOT)" || (echo "BMA456_ROOT is required" >&2; exit 2)
	@test -n "$(LIS2DW12_ROOT)" || (echo "LIS2DW12_ROOT is required" >&2; exit 2)
	@test -n "$(ST25DVXXKC_ROOT)" || (echo "ST25DVXXKC_ROOT is required" >&2; exit 2)
	@test -n "$(TINY_AES_ROOT)" || (echo "TINY_AES_ROOT is required" >&2; exit 2)
	@test -n "$(FLASHDB_ROOT)" || (echo "FLASHDB_ROOT is required" >&2; exit 2)
	$(MAKE) -C platform/nrf52840/sdk SDK_ROOT="$(SDK_ROOT)" \
		BMA456_ROOT="$(BMA456_ROOT)" LIS2DW12_ROOT="$(LIS2DW12_ROOT)" \
		ST25DVXXKC_ROOT="$(ST25DVXXKC_ROOT)" \
		TINY_AES_ROOT="$(TINY_AES_ROOT)" \
		FLASHDB_ROOT="$(FLASHDB_ROOT)" \
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
		--azoteq-settings-root "$(AZOTEQ_SETTINGS_ROOT)"

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

$(ARM_BUILD)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CLANG) $(ARM_FLAGS) -c $< -o $@

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
