# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/startup
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror
.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c initialize.c -o $(OUT)/initialize.o
	$(LD) -T module.ld -o $(OUT)/initialize.elf $(OUT)/initialize.o
.PHONY: itcm
itcm:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c itcm_helpers.S -o $(OUT)/itcm_helpers.o
	$(LD) -T itcm.ld -o $(OUT)/itcm-helpers.elf $(OUT)/itcm_helpers.o
.PHONY: records
records:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c initialize.c -o $(OUT)/initialize.o
	$(CC) $(CFLAGS) -c record_dispatch.c -o $(OUT)/record_dispatch.o
	$(CC) $(CFLAGS) -c record_adapters.S -o $(OUT)/record_adapters.o
	$(CC) $(CFLAGS) -c system_entry.c -o $(OUT)/system_entry.o
	$(CC) $(CFLAGS) -c fpu.S -o $(OUT)/fpu.o
	$(LD) -T records.ld -o $(OUT)/records.elf $(OUT)/initialize.o $(OUT)/record_dispatch.o $(OUT)/record_adapters.o $(OUT)/system_entry.o $(OUT)/fpu.o
.PHONY: reset-source
reset-source:
	$(MAKE) records CPU=cortex-m55 OUT=$(OUT)
	$(CC) $(CFLAGS) -mcpu=cortex-m55 -c reset.S -o $(OUT)/reset.o
	$(LD) -T records.ld -o $(OUT)/reset-source.elf $(OUT)/initialize.o $(OUT)/record_dispatch.o $(OUT)/record_adapters.o $(OUT)/system_entry.o $(OUT)/fpu.o $(OUT)/reset.o
.PHONY: records-table
records-table:
	$(MAKE) records CPU=$(CPU) OUT=$(OUT)
	$(CC) $(CFLAGS) -c init_records.S -o $(OUT)/init_records.o
	$(LD) -T records_table.ld -o $(OUT)/records-table.elf $(OUT)/initialize.o $(OUT)/record_dispatch.o $(OUT)/record_adapters.o $(OUT)/system_entry.o $(OUT)/fpu.o $(OUT)/init_records.o
