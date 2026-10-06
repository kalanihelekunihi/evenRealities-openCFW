# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/mspi
UPSTREAM = ../../../analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c99 -O2 -ffunction-sections -fdata-sections -I$(UPSTREAM)/ambiqhal/mcu/apollo510 -I$(UPSTREAM)/ambiqhal/CMSIS/AmbiqMicro/Include -I$(UPSTREAM)/cmsis-5-590/CMSIS/Core/Include
.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c interrupt.c -o $(OUT)/interrupt.o
	$(CC) $(CFLAGS) -c $(UPSTREAM)/ambiqhal/mcu/apollo510/hal/mcu/am_hal_mspi.c -o $(OUT)/am_hal_mspi.o
	$(LD) --gc-sections -T module.ld -o $(OUT)/mspi.elf $(OUT)/interrupt.o $(OUT)/am_hal_mspi.o
