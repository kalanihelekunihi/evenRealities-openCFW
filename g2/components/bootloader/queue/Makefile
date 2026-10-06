CC = clang
LD = arm-none-eabi-ld
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/queue-wrappers
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c queue_wrappers.c -o $(OUT)/queue_wrappers.o
	$(LD) -T module.ld -o $(OUT)/queue_wrappers.elf $(OUT)/queue_wrappers.o

.PHONY: real-runtime
real-runtime: all
	$(CC) $(CFLAGS) -c runtime_mode.c -o $(OUT)/runtime_mode.o
	$(LD) -T runtime_module.ld -o $(OUT)/queue-runtime.elf $(OUT)/queue_wrappers.o $(OUT)/runtime_mode.o

.PHONY: mutex-runtime
mutex-runtime: real-runtime
	$(CC) $(CFLAGS) -c mutex.c -o $(OUT)/mutex.o
	$(LD) -T mutex_runtime_module.ld -o $(OUT)/mutex-runtime.elf $(OUT)/queue_wrappers.o $(OUT)/runtime_mode.o $(OUT)/mutex.o
