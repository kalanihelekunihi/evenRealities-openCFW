CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
ROOT := ../../../../../
COMP := $(ROOT)/g2/components/bootloader/nor_mspi_init
OUT ?= out
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all verify
all: $(OUT)/register-id.elf

$(OUT):
	mkdir -p $@

$(OUT)/register_id.o: $(COMP)/register_id.c $(COMP)/register_id.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMP) -c $< -o $@

$(OUT)/register-id.elf: $(OUT)/register_id.o register_id.ld
	$(LD) --gc-sections -T register_id.ld -o $@ $(OUT)/register_id.o

verify: $(OUT)/register-id.elf
	$(PYTHON) verify_register_id.py --elf $(OUT)/register-id.elf --output $(OUT)/comparison.json
