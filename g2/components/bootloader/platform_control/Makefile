# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/platform-control
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror
.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c control.c -o $(OUT)/control.o
	$(LD) -T module.ld -o $(OUT)/control.elf $(OUT)/control.o

.PHONY: rom-bridge
rom-bridge: all
	$(CC) $(CFLAGS) -c mram_rom_bridge.c -o $(OUT)/mram_rom_bridge.o
	$(LD) -T rom_module.ld -o $(OUT)/control-rom.elf $(OUT)/control.o $(OUT)/mram_rom_bridge.o

.PHONY: critical-bridge
critical-bridge: rom-bridge
	$(CC) $(CFLAGS) -c critical_save.S -o $(OUT)/critical_save.o
	$(LD) -T critical_rom_module.ld -o $(OUT)/control-critical-rom.elf $(OUT)/control.o $(OUT)/mram_rom_bridge.o $(OUT)/critical_save.o

.PHONY: power-guards
power-guards: critical-bridge
	$(CC) $(CFLAGS) -c power_guards.c -o $(OUT)/power_guards.o
	$(LD) -T power_critical_rom_module.ld -o $(OUT)/control-power-critical-rom.elf $(OUT)/control.o $(OUT)/mram_rom_bridge.o $(OUT)/critical_save.o $(OUT)/power_guards.o
