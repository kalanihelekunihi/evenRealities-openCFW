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
all: $(OUT)/device-info-dispatch.elf

$(OUT):
	mkdir -p $@

$(OUT)/device_info_dispatch.o: $(COMP)/device_info_dispatch.c $(COMP)/device_info_dispatch.h $(COMP)/device_info.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/device_info.o: $(COMP)/device_info.c $(COMP)/device_info.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/device_info_mode0.o: $(COMP)/device_info_mode0.c $(COMP)/device_info_mode0.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/device_mode_wait.o: $(COMP)/device_mode_wait.c $(COMP)/device_mode_wait.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/storage_callbacks.o: $(COMP)/storage_callbacks.c $(COMP)/storage_callbacks.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/device-info-dispatch.elf: $(OUT)/device_info_dispatch.o $(OUT)/device_info.o $(OUT)/device_info_mode0.o $(OUT)/device_mode_wait.o $(OUT)/storage_callbacks.o device_info_dispatch.ld
	$(LD) --gc-sections -T device_info_dispatch.ld -o $@ $(OUT)/device_info_dispatch.o $(OUT)/device_info.o $(OUT)/device_info_mode0.o $(OUT)/device_mode_wait.o $(OUT)/storage_callbacks.o

verify: $(OUT)/device-info-dispatch.elf
	$(PYTHON) verify_device_info_dispatch.py --elf $(OUT)/device-info-dispatch.elf --output $(OUT)/comparison.json
