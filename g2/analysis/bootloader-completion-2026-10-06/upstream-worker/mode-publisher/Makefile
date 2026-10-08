CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
ROOT := ../../../../../
COMP := $(ROOT)/g2/components/bootloader/clock_manager
OUT ?= out
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all verify
all: $(OUT)/mode-publisher.elf

$(OUT):
	mkdir -p $@

$(OUT)/mode_publisher.o: $(COMP)/mode_publisher.c $(COMP)/mode_publisher.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/mode_publisher_abi.o: $(COMP)/mode_publisher_abi.S | $(OUT)
	$(CC) --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -c $< -o $@

$(OUT)/clock_class_providers.o: $(COMP)/clock_class_providers.c $(COMP)/clock_class_providers.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/mode-publisher.elf: $(OUT)/mode_publisher.o $(OUT)/mode_publisher_abi.o $(OUT)/clock_class_providers.o mode_publisher.ld
	$(LD) --gc-sections -T mode_publisher.ld -o $@ $(OUT)/mode_publisher_abi.o $(OUT)/mode_publisher.o $(OUT)/clock_class_providers.o

verify: $(OUT)/mode-publisher.elf
	$(PYTHON) verify_mode_publisher.py --elf $(OUT)/mode-publisher.elf --output $(OUT)/comparison.json
