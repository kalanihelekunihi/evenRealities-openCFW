ROOT := $(abspath ../../../../../)
OUT ?= /tmp/opencfw-pause-dma
CC = clang
LD = arm-none-eabi-ld
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all test
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -I$(ROOT)/g2/components/bootloader/nor_mspi_queue -c $(ROOT)/g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c -o $(OUT)/mspi_pause_dma.o
	$(CC) $(CFLAGS) -c $(ROOT)/g2/components/bootloader/nor_mspi_init/status_poll.c -o $(OUT)/status_poll.o
	$(LD) -T module.ld -o $(OUT)/pause_dma.elf $(OUT)/mspi_pause_dma.o $(OUT)/status_poll.o

test: all
	/Users/kalani/.local/share/opencfw/venv/bin/python verify_pause_dma.py --elf $(OUT)/pause_dma.elf --output $(OUT)/result.json
