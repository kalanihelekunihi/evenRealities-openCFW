COMPONENT := ../../../../components/bootloader/dfu_task
OUT ?= out
CC := clang
LD := arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all test
all: $(OUT)/runtime_context.elf

$(OUT):
	mkdir -p $@

$(OUT)/runtime_context.o: $(COMPONENT)/runtime_context.c $(COMPONENT)/runtime_context.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENT) -c $< -o $@

$(OUT)/runtime_context.elf: $(OUT)/runtime_context.o runtime_context_test.ld
	$(LD) -T runtime_context_test.ld -o $@ $(OUT)/runtime_context.o

test: $(OUT)/runtime_context.elf
	$(PYTHON) verify_runtime_context.py --elf $< --output $(OUT)/comparison.json
