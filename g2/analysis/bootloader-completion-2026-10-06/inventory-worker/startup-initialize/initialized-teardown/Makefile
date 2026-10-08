CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
BUILD ?= /tmp/opencfw-root-pcm22-relocated
ROOT := ../../../../../..
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=softfp -ffreestanding -fno-builtin -ffunction-sections -fdata-sections -O1 -Wall -Wextra
.PHONY: all verify
all:
	mkdir -p $(BUILD)
	$(CLANG) $(CFLAGS) -c teardown.c -o $(BUILD)/teardown.o
	$(CLANG) $(CFLAGS) -c $(ROOT)/g2/components/bootloader/dfu_task/context.c -o $(BUILD)/dfu_context.o
	$(CLANG) $(CFLAGS) -c external_boundary.S -o $(BUILD)/teardown_boundary.o
	$(LD) --gc-sections -T module.ld --undefined=opencfw_boot_dfu_thread_deinit -o $(BUILD)/teardown-addon.elf $(BUILD)/teardown.o $(BUILD)/dfu_context.o $(BUILD)/teardown_boundary.o
verify: all
	$(PYTHON) verify.py --elf $(BUILD)/teardown-addon.elf
