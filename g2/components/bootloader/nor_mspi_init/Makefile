# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= python3
CPU ?= cortex-m4
OUT ?= ../../../build/bootloader-completion/nor-mspi-init
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -fshort-enums -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all verify
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_mspi_init.c -o $(OUT)/nor_mspi_init.o
	$(LD) -T module.ld -o $(OUT)/nor-mspi-init.elf $(OUT)/nor_mspi_init.o

verify: all
	$(PYTHON) verify_nor_mspi_init.py --elf $(OUT)/nor-mspi-init.elf --output $(OUT)/comparison.json
