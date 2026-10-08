CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
ROOT := ../../../../../../
COMP := $(ROOT)/g2/components/bootloader/application_storage
OUT ?= out
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all verify
all: $(OUT)/device-wait-service.elf

$(OUT):
	mkdir -p $@

$(OUT)/device_wait_service.o: $(COMP)/device_wait_service.c $(COMP)/device_wait_service.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/info_read_rom_thunk.o: $(COMP)/info_read_rom_thunk.S | $(OUT)
	$(CC) --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -c $< -o $@

$(OUT)/device-wait-service.elf: $(OUT)/device_wait_service.o $(OUT)/info_read_rom_thunk.o device_wait_service.ld
	$(LD) --gc-sections -T device_wait_service.ld -o $@ $(OUT)/device_wait_service.o $(OUT)/info_read_rom_thunk.o

verify: $(OUT)/device-wait-service.elf
	$(PYTHON) verify_device_wait_service.py --elf $(OUT)/device-wait-service.elf --output $(OUT)/comparison.json
