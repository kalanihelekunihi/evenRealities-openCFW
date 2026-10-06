# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= python3
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/main-init
COMPAT_OUT ?= ../../../build/bootloader-completion/main-init/startup-main-init-compatible
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all verify startup-integrated startup-integrated-compatible verify-startup-integrated
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c main_init.c -o $(OUT)/main_init.o
	$(LD) -T module.ld -o $(OUT)/main-init.elf $(OUT)/main_init.o

verify: all
	$(PYTHON) verify_main_init.py --elf $(OUT)/main-init.elf --output $(OUT)/main-init-comparison.json

startup-integrated:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c ../startup/initialize.c -o $(OUT)/integrated_initialize.o
	$(CC) $(CFLAGS) -c ../startup/record_dispatch.c -o $(OUT)/integrated_record_dispatch.o
	$(CC) $(CFLAGS) -c ../startup/record_adapters.S -o $(OUT)/integrated_record_adapters.o
	$(CC) $(CFLAGS) -c ../startup/system_entry.c -o $(OUT)/integrated_system_entry.o
	$(CC) $(CFLAGS) -c main_init.c -o $(OUT)/integrated_main_init.o
	$(LD) -T startup_integrated.ld -o $(OUT)/startup-main-init.elf $(OUT)/integrated_initialize.o $(OUT)/integrated_record_dispatch.o $(OUT)/integrated_record_adapters.o $(OUT)/integrated_system_entry.o $(OUT)/integrated_main_init.o

startup-integrated-compatible:
	$(MAKE) startup-integrated CPU=cortex-m4 OUT=$(COMPAT_OUT)

verify-startup-integrated: startup-integrated-compatible
	$(PYTHON) verify_startup_integrated.py --elf $(COMPAT_OUT)/startup-main-init.elf --output $(COMPAT_OUT)/comparison-final.json
