CC = clang
LD = arm-none-eabi-ld
PYTHON = /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -Wall -Wextra -Werror -ffunction-sections -fdata-sections
ROOT = ../../../../..
TDIR = $(ROOT)/g2/components/bootloader/thread_creation
QDIR = $(ROOT)/g2/components/bootloader/queue
OUT = out

all: $(OUT)/timer-commands.elf

$(OUT):
	mkdir -p $(OUT)

$(OUT)/timer_commands.o: $(TDIR)/timer_commands.c $(TDIR)/timer_commands.h | $(OUT)
	$(CC) $(CFLAGS) -I$(TDIR) -c $< -o $@

$(OUT)/timer_wait.o: $(TDIR)/timer_wait.c $(TDIR)/timer_wait.h | $(OUT)
	$(CC) $(CFLAGS) -I$(TDIR) -c $< -o $@

$(OUT)/queue_receive.o: $(TDIR)/queue_receive.c $(TDIR)/queue_receive.h | $(OUT)
	$(CC) $(CFLAGS) -I$(TDIR) -c $< -o $@

$(OUT)/fixture_providers.o: fixture_providers.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/kernel_runtime.o: $(TDIR)/kernel_runtime.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/runtime_mode.o: $(QDIR)/runtime_mode.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/timer-commands.elf: $(OUT)/timer_commands.o $(OUT)/timer_wait.o $(OUT)/queue_receive.o $(OUT)/kernel_runtime.o $(OUT)/runtime_mode.o $(OUT)/fixture_providers.o module.ld
	$(LD) --gc-sections -T module.ld -Map=$(OUT)/timer-commands.map -o $@ $(filter %.o,$^)

verify: all
	$(PYTHON) verify_timer_commands.py --elf $(OUT)/timer-commands.elf --output $(OUT)/comparison.json

.PHONY: all verify

# Common regression aggregate entry; verify performs the instruction comparison.
.PHONY: test
test: verify
