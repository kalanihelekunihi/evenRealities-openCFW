# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/dfu-task
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -I../filesystem/freestanding_include
.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c task.c -o $(OUT)/task.o
	$(CC) $(CFLAGS) -c ../filesystem/runtime_memory.c -o $(OUT)/runtime_memory.o
	$(LD) -T module.ld -o $(OUT)/task.elf $(OUT)/task.o $(OUT)/runtime_memory.o

.PHONY: context
context:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c context.c -o $(OUT)/context.o
	$(LD) -T context_module.ld -o $(OUT)/context.elf $(OUT)/context.o
