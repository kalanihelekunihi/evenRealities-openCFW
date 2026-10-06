ROOT := ../../../../../
UPSTREAM := $(ROOT)/g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510
OUT ?= out
CC = clang
LD = arm-none-eabi-ld
NM = arm-none-eabi-nm
CPU ?= cortex-m55
CFLAGS := --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections -O2
INCLUDES := -I$(UPSTREAM)/ambiqhal/mcu/apollo510 \
	-I$(UPSTREAM)/ambiqhal/CMSIS/AmbiqMicro/Include \
	-I$(UPSTREAM)/cmsis-5-590/CMSIS/Core/Include

.PHONY: all clean
all: $(OUT)/mspi-setup-provider-closure.o $(OUT)/undefined-symbols.txt $(OUT)/layout_probe.o

$(OUT):
	mkdir -p $@

$(OUT)/am_hal_mspi.o: $(UPSTREAM)/ambiqhal/mcu/apollo510/hal/mcu/am_hal_mspi.c | $(OUT)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(OUT)/call_slice.o: call_slice.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/layout_probe.o: layout_probe.c | $(OUT)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(OUT)/mspi-setup-provider-closure.o: $(OUT)/call_slice.o $(OUT)/am_hal_mspi.o
	$(LD) -r --gc-sections -u opencfw_mspi_nor_setup_slice $^ -o $@

$(OUT)/undefined-symbols.txt: $(OUT)/mspi-setup-provider-closure.o
	$(NM) -u $< | sed 's/^[[:space:]]*U //' | sort -u > $@

clean:
	rm -rf $(OUT)
