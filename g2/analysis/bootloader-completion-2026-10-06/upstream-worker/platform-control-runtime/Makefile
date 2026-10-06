CC = clang
LD = arm-none-eabi-ld
PYTHON = /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -ffunction-sections -fdata-sections
ROOT = ../../../../..
PCDIR = $(ROOT)/g2/components/bootloader/platform_control
CDIR = $(ROOT)/g2/components/bootloader/clock_manager
OUT = out

all: $(OUT)/platform-control-runtime.elf

$(OUT):
	mkdir -p $(OUT)

$(OUT)/runtime.o: $(PCDIR)/runtime.c $(PCDIR)/runtime.h | $(OUT)
	$(CC) $(CFLAGS) -I$(PCDIR) -I$(CDIR) -c $< -o $@

$(OUT)/runtime-transition.o: $(PCDIR)/runtime_transition.c $(PCDIR)/runtime_transition.h | $(OUT)
	$(CC) $(CFLAGS) -I$(PCDIR) -I$(CDIR) -c $< -o $@

$(OUT)/runtime-query.o: $(PCDIR)/runtime_query.c $(PCDIR)/runtime_query.h | $(OUT)
	$(CC) $(CFLAGS) -I$(PCDIR) -I$(CDIR) -c $< -o $@

$(OUT)/clock-register.o: $(CDIR)/clock_class_providers.c | $(OUT)
	$(CC) $(CFLAGS) -I$(CDIR) -c $< -o $@

$(OUT)/fixture_apply.o: fixture_apply.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/critical-save.o: $(PCDIR)/critical_save.S | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/platform-control-runtime.elf: $(OUT)/runtime.o $(OUT)/runtime-transition.o $(OUT)/runtime-query.o $(OUT)/clock-register.o $(OUT)/fixture_apply.o $(OUT)/critical-save.o module.ld
	$(LD) --gc-sections -T module.ld -Map=$(OUT)/platform-control-runtime.map -o $@ $(filter %.o,$^)

verify: all
	$(PYTHON) verify_runtime.py --elf $(OUT)/platform-control-runtime.elf --output $(OUT)/mode-one.json

.PHONY: all verify
