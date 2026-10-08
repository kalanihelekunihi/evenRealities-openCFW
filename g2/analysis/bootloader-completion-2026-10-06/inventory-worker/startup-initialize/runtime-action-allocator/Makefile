PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CLANG ?= clang
ARM_LD ?= arm-none-eabi-ld
ROOT := ../../../../../..
SOURCE_DIR := $(ROOT)/g2/components/bootloader/thread_creation
BUILD := out
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=softfp -ffreestanding -fno-builtin -ffunction-sections -fdata-sections -fno-unwind-tables -fno-asynchronous-unwind-tables -O1 -Wall -Wextra

.PHONY: test clean
test: $(BUILD)/fixture.elf
	$(PYTHON) verify.py --elf $(BUILD)/fixture.elf --output comparison.json

$(BUILD):
	mkdir -p $@

$(BUILD)/runtime_action.o: ../runtime-action-416200/runtime_action.c Makefile | $(BUILD)
	$(CLANG) $(CFLAGS) -c $< -o $@

$(BUILD)/rtos_heap.o: $(SOURCE_DIR)/rtos_heap.c Makefile | $(BUILD)
	$(CLANG) $(CFLAGS) -c $< -o $@

$(BUILD)/platform_cuts.o: platform_cuts.c Makefile | $(BUILD)
	$(CLANG) $(CFLAGS) -c $< -o $@

$(BUILD)/fixture.elf: $(BUILD)/runtime_action.o $(BUILD)/rtos_heap.o $(BUILD)/platform_cuts.o module.ld Makefile
	$(ARM_LD) --gc-sections -T module.ld -o $@ $(BUILD)/runtime_action.o $(BUILD)/rtos_heap.o $(BUILD)/platform_cuts.o

clean:
	rm -rf $(BUILD) comparison.json comparison.failure.json
