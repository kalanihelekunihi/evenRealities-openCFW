ROOT := ../../../../../
COMPONENT := ../../../../components/bootloader/clock_manager
PROVIDER_COMPONENT := $(COMPONENT)
OUT ?= out
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-fshort-enums -std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all test clean
all: $(OUT)/clock_manager.elf

$(OUT):
	mkdir -p $@

$(OUT)/clock_manager.o: $(COMPONENT)/clock_manager.c $(COMPONENT)/clock_manager.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENT) -c $(COMPONENT)/clock_manager.c -o $@

$(OUT)/clock_class_providers.o: $(PROVIDER_COMPONENT)/clock_class_providers.c $(PROVIDER_COMPONENT)/clock_class_providers.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENT) -c $(PROVIDER_COMPONENT)/clock_class_providers.c -o $@

$(OUT)/provider_stubs.o: provider_test_stubs.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/clock_manager.elf: $(OUT)/clock_manager.o $(OUT)/clock_class_providers.o $(OUT)/provider_stubs.o clock_manager_test.ld
	$(LD) -T clock_manager_test.ld -o $@ $(OUT)/clock_manager.o $(OUT)/clock_class_providers.o $(OUT)/provider_stubs.o

test: $(OUT)/clock_manager.elf
	$(PYTHON) verify_clock_manager.py --elf $< --output $(OUT)/comparison.json

clean:
	rm -rf $(OUT)
