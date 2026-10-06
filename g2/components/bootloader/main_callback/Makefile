# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/main-callback
COMPAT_OUT ?= ../../../build/bootloader-completion/main-callback-compatible
INTEGRATED_OUT ?= ../../../build/bootloader-completion/main-callback-startup-integrated-compatible
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror
M4_CFLAGS = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all verify compatible verify-compatible startup-integrated-compatible verify-startup-integrated-compatible
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c main_callback.c -o $(OUT)/main_callback.o
	$(LD) -T module.ld -o $(OUT)/main-callback.elf $(OUT)/main_callback.o

verify: all
	$(PYTHON) verify_main_callback.py --elf $(OUT)/main-callback.elf --output $(OUT)/comparison-first.json

compatible:
	$(MAKE) all CPU=cortex-m4 OUT=$(COMPAT_OUT)

verify-compatible: compatible
	$(PYTHON) verify_main_callback.py --elf $(COMPAT_OUT)/main-callback.elf --output $(COMPAT_OUT)/comparison-first.json

startup-integrated-compatible:
	mkdir -p $(INTEGRATED_OUT)
	$(CC) $(M4_CFLAGS) -c ../startup/initialize.c -o $(INTEGRATED_OUT)/initialize.o
	$(CC) $(M4_CFLAGS) -c ../startup/record_dispatch.c -o $(INTEGRATED_OUT)/record_dispatch.o
	$(CC) $(M4_CFLAGS) -c ../startup/record_adapters.S -o $(INTEGRATED_OUT)/record_adapters.o
	$(CC) $(M4_CFLAGS) -c ../startup/system_entry.c -o $(INTEGRATED_OUT)/system_entry.o
	$(CC) $(M4_CFLAGS) -c ../startup/init_records.S -o $(INTEGRATED_OUT)/init_records.o
	$(CC) $(M4_CFLAGS) -c ../main_init/main_init.c -o $(INTEGRATED_OUT)/main_init.o
	$(CC) $(M4_CFLAGS) -DOPENCFW_MAIN_CALLBACK_AT_STOCK_ADDRESS -c main_callback.c -o $(INTEGRATED_OUT)/main_callback.o
	$(LD) -T startup_callback_integrated.ld -o $(INTEGRATED_OUT)/startup-main-callback.elf $(INTEGRATED_OUT)/initialize.o $(INTEGRATED_OUT)/record_dispatch.o $(INTEGRATED_OUT)/record_adapters.o $(INTEGRATED_OUT)/system_entry.o $(INTEGRATED_OUT)/init_records.o $(INTEGRATED_OUT)/main_init.o $(INTEGRATED_OUT)/main_callback.o

verify-startup-integrated-compatible: startup-integrated-compatible
	$(PYTHON) verify_startup_callback_integrated.py --elf $(INTEGRATED_OUT)/startup-main-callback.elf --output $(INTEGRATED_OUT)/comparison-first.json
