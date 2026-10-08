ROOT := $(abspath ../../../../../)
OUT ?= /tmp/opencfw-queue-descriptors
CC = clang
LD = arm-none-eabi-ld
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all test
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -I$(ROOT)/g2/components/bootloader/nor_mspi_queue -c $(ROOT)/g2/components/bootloader/nor_mspi_queue/queue_descriptors.c -o $(OUT)/queue_descriptors.o
	$(LD) -T module.ld -o $(OUT)/queue_descriptors.elf $(OUT)/queue_descriptors.o

test: all
	/Users/kalani/.local/share/opencfw/venv/bin/python verify_queue_descriptors.py --elf $(OUT)/queue_descriptors.elf --output $(OUT)/result.json
