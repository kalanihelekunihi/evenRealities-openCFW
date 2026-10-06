# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
OUT ?= ../../../build/bootloader-completion/update-core
CPU ?= cortex-m55
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -Wall -Wextra -Werror -O2 -fwrapv
.PHONY: all
all: $(OUT)/update-core.elf
$(OUT)/update-core.elf: update_core.c update_core.h handoff.S rom_resources.c module.ld
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c update_core.c -o $(OUT)/update_core.o
	$(CC) $(CFLAGS) -c handoff.S -o $(OUT)/handoff.o
	$(CC) $(CFLAGS) -c rom_resources.c -o $(OUT)/rom_resources.o
	$(LD) -T module.ld -o $@ $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o
