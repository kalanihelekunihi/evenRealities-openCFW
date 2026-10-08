CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
ROOT := ../../../../../
COMP := $(ROOT)/g2/components/bootloader/nor_mspi_power
OUT ?= out
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all verify
all: $(OUT)/nor-mode-switch.elf

$(OUT):
	mkdir -p $@

$(OUT)/serial_mode_switch.o: $(COMP)/serial_mode_switch.c $(COMP)/serial_mode_switch.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/nor-mode-switch.elf: $(OUT)/serial_mode_switch.o mode_switch.ld
	$(LD) --gc-sections -T mode_switch.ld -o $@ $(OUT)/serial_mode_switch.o

verify: $(OUT)/nor-mode-switch.elf
	$(PYTHON) verify_mode_switch.py --elf $(OUT)/nor-mode-switch.elf --output $(OUT)/differential.json
