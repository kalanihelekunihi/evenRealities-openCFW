ROOT := ../../../../../
OUT ?= out
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= python3
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-fshort-enums -std=c11 -O2 -Wall -Wextra -Werror
INCLUDES := -I$(ROOT)/g2/components/foundation/ambiq_mspi

.PHONY: all clean test
all: $(OUT)/mspi_enable.elf

$(OUT):
	mkdir -p $@

$(OUT)/enable.o: am_hal_mspi_enable.c | $(OUT)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(OUT)/cq_stub.o: cq_stub.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/mspi_enable.elf: $(OUT)/enable.o $(OUT)/cq_stub.o module.ld
	$(LD) -T module.ld -o $@ $(OUT)/enable.o $(OUT)/cq_stub.o

test: $(OUT)/mspi_enable.elf
	$(PYTHON) verify_enable.py --elf $(OUT)/mspi_enable.elf --output $(OUT)/comparison.json

clean:
	rm -rf $(OUT)
