ROOT := $(abspath ../../../../../)
OUT ?= /tmp/opencfw-control-request-helpers
CC = clang
LD = arm-none-eabi-ld
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -fwrapv -Wall -Wextra -Werror
COMP = $(ROOT)/g2/components/bootloader/nor_mspi_init

.PHONY: all test
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c $(COMP)/control_request_helpers.c -o $(OUT)/control_request_helpers.o
	$(LD) --gc-sections -u opencfw_provider_427c12 -u opencfw_provider_4279be -T module.ld -o $(OUT)/control_request_helpers.elf $(OUT)/control_request_helpers.o

test: all
	/Users/kalani/.local/share/opencfw/venv/bin/python verify_control_request_helpers.py --elf $(OUT)/control_request_helpers.elf --output $(OUT)/result.json
