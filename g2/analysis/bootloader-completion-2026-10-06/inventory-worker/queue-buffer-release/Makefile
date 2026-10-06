CC = clang
LD = arm-none-eabi-ld
PYTHON = /Users/kalani/.local/share/opencfw/venv/bin/python
CPU = cortex-m4
OUT ?= ../../../../build/bootloader-completion/queue-buffer-release
ROOT = ../../../../..
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -I$(ROOT)/g2/components/bootloader/thread_creation
.PHONY: all verify
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c $(ROOT)/g2/components/bootloader/thread_creation/queue_buffer_release.c -o $(OUT)/queue_buffer_release.o
	$(LD) -T queue_buffer_release_module.ld -o $(OUT)/queue-buffer-release.elf $(OUT)/queue_buffer_release.o
verify: all
	$(PYTHON) verify_queue_buffer_release.py --elf $(OUT)/queue-buffer-release.elf --output queue-buffer-release-comparison.json
