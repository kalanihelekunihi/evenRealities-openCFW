# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON = /Users/kalani/.local/share/opencfw/venv/bin/python
CPU ?= cortex-m4
OUT ?= ../../../build/bootloader-completion/nor-commands
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -fshort-enums -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all verify
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_commands.c -o $(OUT)/nor_commands.o
	$(CC) --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -c nor_timing_wrapper.S -o $(OUT)/nor_timing_wrapper.o
	$(LD) -T module.ld -o $(OUT)/nor-commands.elf $(OUT)/nor_commands.o $(OUT)/nor_timing_wrapper.o

verify: all
	$(PYTHON) ../../../../g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-commands/verify_nor_commands.py --elf $(OUT)/nor-commands.elf --output ../../../../g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-commands/nor-commands-comparison.json
