# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m4
OUT ?= ../../../build/bootloader-completion/nor-mspi-queue
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -fshort-enums -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_mspi_queue.c -o $(OUT)/nor_mspi_queue.o
	$(CC) $(CFLAGS) -c resources.c -o $(OUT)/resources.o
	$(LD) -T module.ld -o $(OUT)/nor_mspi_queue.elf $(OUT)/nor_mspi_queue.o $(OUT)/resources.o
