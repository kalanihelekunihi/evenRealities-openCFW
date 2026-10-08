# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= python3
ROOT := ../../../../../
COMPONENTS := $(ROOT)/g2/components/bootloader
OUT ?= out
CPU ?= cortex-m4
CFLAGS := --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all verify
all: $(OUT)/application-storage.elf

$(OUT):
	mkdir -p $@

$(OUT)/application-storage.elf: $(OUT)/initialize.o $(OUT)/record_dispatch.o \
		$(OUT)/record_adapters.o $(OUT)/system_entry.o $(OUT)/main_init.o \
		$(OUT)/platform_startup.o $(OUT)/platform_control_runtime.o \
		$(OUT)/clock_class_providers.o $(OUT)/storage_callbacks.o \
		$(OUT)/storage_callback_veneers.o \
		$(OUT)/control.o $(OUT)/power_guards.o $(OUT)/mram_rom_bridge.o \
		$(OUT)/critical_save.o $(OUT)/test_cuts.o application_storage.ld | $(OUT)
	$(LD) --gc-sections -T application_storage.ld -o $@ \
		$(filter %.o,$^)

$(OUT)/initialize.o: $(COMPONENTS)/startup/initialize.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/startup -c $< -o $@
$(OUT)/record_dispatch.o: $(COMPONENTS)/startup/record_dispatch.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/startup -c $< -o $@
$(OUT)/record_adapters.o: $(COMPONENTS)/startup/record_adapters.S | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@
$(OUT)/system_entry.o: $(COMPONENTS)/startup/system_entry.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/startup -c $< -o $@
$(OUT)/main_init.o: $(COMPONENTS)/main_init/main_init.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@
$(OUT)/platform_startup.o: $(COMPONENTS)/platform_startup/platform_startup.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/platform_startup -c $< -o $@
$(OUT)/platform_control_runtime.o: $(COMPONENTS)/platform_control/runtime.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/platform_control -c $< -o $@
$(OUT)/clock_class_providers.o: $(COMPONENTS)/clock_manager/clock_class_providers.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/clock_manager -c $< -o $@
$(OUT)/storage_callbacks.o: $(COMPONENTS)/application_storage/storage_callbacks.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/application_storage -c $< -o $@
$(OUT)/storage_callback_veneers.o: $(COMPONENTS)/application_storage/storage_callback_veneers.S | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@
$(OUT)/control.o: $(COMPONENTS)/platform_control/control.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENTS)/platform_control -c $< -o $@
$(OUT)/power_guards.o: $(COMPONENTS)/platform_control/power_guards.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@
$(OUT)/mram_rom_bridge.o: $(COMPONENTS)/platform_control/mram_rom_bridge.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@
$(OUT)/critical_save.o: $(COMPONENTS)/platform_control/critical_save.S | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@
$(OUT)/test_cuts.o: test_cuts.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

verify: $(OUT)/application-storage.elf
	$(PYTHON) verify_application_storage.py --elf $(OUT)/application-storage.elf --output $(OUT)/comparison.json
