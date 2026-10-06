# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/allocator
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -DNDEBUG -I. -Ifreestanding_include -I../filesystem/freestanding_include
.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c allocator.c -o $(OUT)/allocator.o
	$(CC) $(CFLAGS) -c upstream/tlsf.c -o $(OUT)/tlsf.o
	$(CC) $(CFLAGS) -c ../filesystem/runtime_memory.c -o $(OUT)/runtime_memory.o
	$(LD) -T module.ld -o $(OUT)/allocator.elf $(OUT)/allocator.o $(OUT)/tlsf.o $(OUT)/runtime_memory.o
