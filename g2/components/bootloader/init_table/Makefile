# SPDX-License-Identifier: MIT
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= python3
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror

.PHONY: all verify
all:
	mkdir -p ../../../build/bootloader-completion/init-table-review
	$(CC) $(CFLAGS) -c init_table.c -o ../../../build/bootloader-completion/init-table-review/init_table.o
	$(CC) $(CFLAGS) -c qsort.c -o ../../../build/bootloader-completion/init-table-review/qsort.o
	$(LD) -T module.ld -o ../../../build/bootloader-completion/init-table-review/init-table.elf ../../../build/bootloader-completion/init-table-review/init_table.o ../../../build/bootloader-completion/init-table-review/qsort.o

verify: all
	$(PYTHON) verify_init_table.py --elf ../../../build/bootloader-completion/init-table-review/init-table.elf --output ../../../analysis/bootloader-completion-2026-10-06/review-worker/init-table-runner/comparison.json
