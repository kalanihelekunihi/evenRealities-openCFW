CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../../build/bootloader-completion/nor-read-setup
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -fshort-enums -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all linked-status
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_read_setup.c -o $(OUT)/nor_read_setup.o
	$(LD) -T module.ld -o $(OUT)/nor_read_setup.elf $(OUT)/nor_read_setup.o

linked-status:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c nor_read_setup.c -o $(OUT)/nor_read_setup_linked.o
	$(CC) $(filter-out -mcpu=$(CPU),$(CFLAGS)) -mcpu=cortex-m4 -c ../nor-read-status/nor_read_status.c -o $(OUT)/nor_read_status.o
	$(LD) -T module-linked-status.ld -o $(OUT)/nor_read_setup_status.elf $(OUT)/nor_read_setup_linked.o $(OUT)/nor_read_status.o
