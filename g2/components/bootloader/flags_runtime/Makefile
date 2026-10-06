# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON = /Users/kalani/.local/share/opencfw/venv/bin/python
CPU = cortex-m4
OUT ?= ../../../build/bootloader-completion/flags-runtime
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all verify
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c flags_runtime.c -o $(OUT)/flags_runtime.o
	$(CC) $(CFLAGS) -c cmsis_notifications.c -o $(OUT)/cmsis_notifications.o
	$(LD) -T module.ld -o $(OUT)/flags-runtime.elf $(OUT)/flags_runtime.o $(OUT)/cmsis_notifications.o

verify: all
	$(PYTHON) ../../../../g2/analysis/bootloader-completion-2026-10-06/inventory-worker/flags-runtime/verify_flags_runtime.py --elf $(OUT)/flags-runtime.elf --output ../../../../g2/analysis/bootloader-completion-2026-10-06/inventory-worker/flags-runtime/flags-runtime-comparison.json
	$(PYTHON) ../../../../g2/analysis/bootloader-completion-2026-10-06/inventory-worker/flags-runtime/verify_cmsis_notifications.py --elf $(OUT)/flags-runtime.elf --output ../../../../g2/analysis/bootloader-completion-2026-10-06/inventory-worker/flags-runtime/cmsis-notifications-comparison.json
