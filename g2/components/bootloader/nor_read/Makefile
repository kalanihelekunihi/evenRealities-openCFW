CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/nor-read
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -fshort-enums -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_read.c -o $(OUT)/nor_read.o
	$(LD) -T module.ld -o $(OUT)/nor_read.elf $(OUT)/nor_read.o

PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
.PHONY: helpers-compatible
helpers-compatible:
	mkdir -p ../../../build/bootloader-completion/nor-read-helpers
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c runtime_helpers.c -o ../../../build/bootloader-completion/nor-read-helpers/helpers.o
	$(LD) -T helpers_module.ld -o ../../../build/bootloader-completion/nor-read-helpers/helpers.elf ../../../build/bootloader-completion/nor-read-helpers/helpers.o
	$(PYTHON) verify_helpers.py --elf ../../../build/bootloader-completion/nor-read-helpers/helpers.elf --output ../../../build/bootloader-completion/nor-read-helpers/comparison.json
