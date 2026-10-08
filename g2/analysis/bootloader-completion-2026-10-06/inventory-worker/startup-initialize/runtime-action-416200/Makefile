CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
ROOT := ../../../../../..
BASE := $(ROOT)/g2/build/bootloader-completion/startup-pcm22-handler17-integrated/687b0a4e3ce6aef856d19738977a8285033a36110c629d73b0b3cc7306da187d/candidate17-integrated.elf
BUILD := /tmp/opencfw-root-pcm22-handler17-validation
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=softfp -ffreestanding -fno-builtin -ffunction-sections -fdata-sections -O1 -Wall -Wextra
.PHONY: all verify
all:
	mkdir -p $(BUILD)
	$(CLANG) $(CFLAGS) -c runtime_action.c -o $(BUILD)/runtime_action.o
	$(LD) --gc-sections -T module.ld --just-symbols=$(BASE) -o $(BUILD)/runtime-action-addon.elf $(BUILD)/runtime_action.o
verify: all
	$(PYTHON) verify.py --addon $(BUILD)/runtime-action-addon.elf

.PHONY: callers verify-callers
callers: all
	$(CLANG) $(CFLAGS) -c ../initialized-teardown/teardown.c -o $(BUILD)/teardown.o
	$(CLANG) $(CFLAGS) -c $(ROOT)/g2/components/bootloader/dfu_task/context.c -o $(BUILD)/dfu_context.o
	$(CLANG) $(CFLAGS) -c teardown_native_aliases.S -o $(BUILD)/teardown_native_aliases.o
	/opt/homebrew/bin/arm-none-eabi-objcopy --strip-symbol=opencfw_provider_416200 $(BASE) $(BUILD)/base-symbols-without-termination-alias.elf
	$(LD) --gc-sections -T teardown.ld --just-symbols=$(BUILD)/base-symbols-without-termination-alias.elf -o $(BUILD)/teardown-native-addon.elf $(BUILD)/runtime_action.o $(BUILD)/teardown.o $(BUILD)/dfu_context.o $(BUILD)/teardown_native_aliases.o
verify-callers: callers
	$(PYTHON) verify_native_teardown.py --addon $(BUILD)/teardown-native-addon.elf
