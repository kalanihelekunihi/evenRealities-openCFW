CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m4
OUT ?= ../../../../build/bootloader-completion/nor-read-status
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -fshort-enums -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_read_status.c -o $(OUT)/nor_read_status.o
	$(LD) -T module.ld -o $(OUT)/nor_read_status.elf $(OUT)/nor_read_status.o
