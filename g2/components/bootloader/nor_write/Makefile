CC = clang
LD = arm-none-eabi-ld
# Use the baseline Thumb-2 profile supported by the differential runner.
CPU ?= cortex-m4
OUT ?= ../../../build/bootloader-completion/nor-write
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -fshort-enums -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_write.c -o $(OUT)/nor_write.o
	$(LD) -T module.ld -o $(OUT)/nor_write.elf $(OUT)/nor_write.o
