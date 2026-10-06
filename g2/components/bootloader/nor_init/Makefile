# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= python3
CPU ?= cortex-m4
OUT ?= ../../../build/bootloader-completion/nor-init
NOR_STATUS = ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-status/nor_read_status.c
NOR_STATUS_INCLUDE = ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-status
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -fshort-enums -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -I$(NOR_STATUS_INCLUDE)

.PHONY: all verify
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_init.c -o $(OUT)/nor_init.o
	$(CC) $(CFLAGS) -c $(NOR_STATUS) -o $(OUT)/nor_read_status.o
	$(LD) -T module.ld -o $(OUT)/nor-init.elf $(OUT)/nor_init.o $(OUT)/nor_read_status.o

verify: all
	$(PYTHON) verify_nor_init.py --elf $(OUT)/nor-init.elf --output $(OUT)/comparison.json
