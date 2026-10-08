ROOT := $(abspath ../../../../../)
OUT ?= /tmp/opencfw-control-remaining
CC = clang
LD = arm-none-eabi-ld
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -fwrapv -Wall -Wextra -Werror
COMP = $(ROOT)/g2/components/bootloader

.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -c $(COMP)/nor_mspi_init/control_read.c -o $(OUT)/control_read.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -c $(COMP)/nor_mspi_init/control_remaining.c -o $(OUT)/control_remaining.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -I$(COMP)/nor_mspi_queue -c $(COMP)/nor_mspi_init/control_request_extension.c -o $(OUT)/control_request_extension.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -c $(COMP)/nor_mspi_init/control_request_state.c -o $(OUT)/control_request_state.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -I$(COMP)/nor_mspi_power -c $(COMP)/nor_mspi_init/control_request_clock.c -o $(OUT)/control_request_clock.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_queue -c $(COMP)/nor_mspi_queue/queue_descriptors.c -o $(OUT)/queue_descriptors.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_queue -c $(COMP)/nor_mspi_queue/mspi_pause_dma.c -o $(OUT)/mspi_pause_dma.o
	$(CC) $(CFLAGS) -c $(COMP)/platform_control/critical_save.S -o $(OUT)/critical_save.o
	$(CC) $(CFLAGS) -c $(COMP)/nor_mspi_init/status_poll.c -o $(OUT)/status_poll.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_power -c $(COMP)/nor_mspi_power/device_configure.c -o $(OUT)/device_configure.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -c $(COMP)/nor_mspi_init/control_request_helpers.c -o $(OUT)/control_request_helpers.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -c $(COMP)/nor_mspi_init/control_request_transactions.c -o $(OUT)/control_request_transactions.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_init -c $(COMP)/nor_mspi_init/control_request34.c -o $(OUT)/control_request34.o
	$(CC) $(CFLAGS) -I$(COMP)/nor_mspi_queue -c $(COMP)/nor_mspi_queue/nor_mspi_queue.c -o $(OUT)/nor_mspi_queue.o
	$(LD) --gc-sections -T module.ld -o $(OUT)/control_remaining.elf $(OUT)/control_read.o $(OUT)/control_remaining.o $(OUT)/control_request_extension.o $(OUT)/control_request_state.o $(OUT)/control_request_clock.o $(OUT)/queue_descriptors.o $(OUT)/mspi_pause_dma.o $(OUT)/critical_save.o $(OUT)/status_poll.o $(OUT)/device_configure.o $(OUT)/control_request_helpers.o $(OUT)/control_request_transactions.o $(OUT)/control_request34.o $(OUT)/nor_mspi_queue.o

.PHONY: test
test: all
	/Users/kalani/.local/share/opencfw/venv/bin/python verify_control_remaining.py --elf $(OUT)/control_remaining.elf --output $(OUT)/result.json
