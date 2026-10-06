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
all: $(OUT)/platform-startup.elf

$(OUT):
	mkdir -p $@

$(OUT)/platform-startup.elf: $(OUT)/initialize.o $(OUT)/record_dispatch.o \
		$(OUT)/record_adapters.o $(OUT)/system_entry.o $(OUT)/main_init.o \
		$(OUT)/platform_startup.o $(OUT)/platform_control_runtime.o \
		$(OUT)/clock_class_providers.o $(OUT)/provider_cuts.o platform_startup.ld | $(OUT)
	$(LD) --gc-sections -T platform_startup.ld -o $@ \
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
$(OUT)/provider_cuts.o: provider_cuts.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

verify: $(OUT)/platform-startup.elf
	$(PYTHON) verify_platform_startup.py --elf $(OUT)/platform-startup.elf --output $(OUT)/comparison.json
