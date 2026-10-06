ROOT := ../../../../../
OUT ?= out
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= python3
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-fshort-enums -std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all clean test
all: $(OUT)/mspi_cq_init.elf

$(OUT):
	mkdir -p $@

$(OUT)/cq_init.o: mspi_cq_init.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/cmdq_stub.o: cmdq_stub.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/mspi_cq_init.elf: $(OUT)/cq_init.o $(OUT)/cmdq_stub.o module.ld
	$(LD) -T module.ld -o $@ $(OUT)/cq_init.o $(OUT)/cmdq_stub.o

test: $(OUT)/mspi_cq_init.elf
	$(PYTHON) verify_cq_init.py --elf $(OUT)/mspi_cq_init.elf --output $(OUT)/comparison.json

clean:
	rm -rf $(OUT)
