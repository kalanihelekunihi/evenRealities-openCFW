CC = clang
LD = arm-none-eabi-ld
PYTHON = /Users/kalani/.local/share/opencfw/venv/bin/python
CPU = cortex-m4
OUT ?= ../../../../build/bootloader-completion/queue-send
ROOT = ../../../../..
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -I$(ROOT)/g2/components/bootloader/thread_creation
.PHONY: all verify
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c $(ROOT)/g2/components/bootloader/thread_creation/queue_send.c -o $(OUT)/queue_send.o
	$(LD) -T queue_send_module.ld -o $(OUT)/queue-send.elf $(OUT)/queue_send.o
verify: all
	$(PYTHON) verify_queue_send.py --elf $(OUT)/queue-send.elf --output queue-send-comparison.json
