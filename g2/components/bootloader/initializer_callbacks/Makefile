CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror
OUT = ../../../build/bootloader-completion/initializer-callbacks-review

.PHONY: all verify
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c initializer_callbacks.c -o $(OUT)/initializer_callbacks.o
	$(CC) $(CFLAGS) -ffunction-sections -fdata-sections -c ../clock_manager/clock_class_providers.c -o $(OUT)/clock_class_providers.o
	$(CC) $(CFLAGS) -c mode_register.c -o $(OUT)/mode_register.o
	$(CC) $(CFLAGS) -c platform_finish.c -o $(OUT)/platform_finish.o
	$(CC) $(CFLAGS) -c post_bringup.c -o $(OUT)/post_bringup.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -c platform_bringup.c -o $(OUT)/platform_bringup.o
	$(LD) --gc-sections -T module.ld -o $(OUT)/initializer-callbacks.elf $(OUT)/initializer_callbacks.o $(OUT)/clock_class_providers.o $(OUT)/mode_register.o $(OUT)/platform_finish.o $(OUT)/post_bringup.o $(OUT)/platform_bringup.o

verify: all
	$(PYTHON) verify_initializer_callbacks.py --elf $(OUT)/initializer-callbacks.elf --output ../../../analysis/bootloader-completion-2026-10-06/review-worker/initializer-callbacks/comparison.json
