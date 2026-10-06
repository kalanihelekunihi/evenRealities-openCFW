ROOT := ../../../../../
COMPONENT := ../../../../components/bootloader/port_timer
OUT ?= out
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-fshort-enums -std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all test clean
all: $(OUT)/port_timer.elf

$(OUT):
	mkdir -p $@

$(OUT)/port_timer.o: $(COMPONENT)/port_timer.c $(COMPONENT)/port_timer.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENT) -c $(COMPONENT)/port_timer.c -o $@

$(OUT)/clock_stubs.o: clock_provider_stubs.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/port_timer.elf: $(OUT)/port_timer.o $(OUT)/clock_stubs.o port_timer_test.ld
	$(LD) -T port_timer_test.ld -o $@ $(OUT)/port_timer.o $(OUT)/clock_stubs.o

test: $(OUT)/port_timer.elf
	$(PYTHON) verify_port_timer.py --elf $< --output $(OUT)/comparison.json

clean:
	rm -rf $(OUT)
