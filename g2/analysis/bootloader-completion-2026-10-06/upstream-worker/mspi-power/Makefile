ROOT := ../../../../../
OUT ?= out
CC := clang
LD := /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-fshort-enums -std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all test
all: $(OUT)/device_configure.elf $(OUT)/power_control_test.elf

$(OUT):
	mkdir -p $@

$(OUT)/device_configure.o: $(ROOT)/g2/components/bootloader/nor_mspi_power/device_configure.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/mspi_clockgen_control.o: $(ROOT)/g2/components/bootloader/nor_mspi_power/mspi_clockgen_control.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/power_control.o: $(ROOT)/g2/components/bootloader/nor_mspi_power/power_control.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/power_control_adapter.o: $(ROOT)/g2/components/bootloader/nor_mspi_power/power_control_adapter.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/device_configure.elf: $(OUT)/device_configure.o $(OUT)/mspi_clockgen_control.o device_configure_module.ld
	$(LD) -T device_configure_module.ld -o $@ $(OUT)/device_configure.o $(OUT)/mspi_clockgen_control.o

$(OUT)/power_control_test.elf: $(OUT)/power_control.o $(OUT)/power_control_adapter.o module.ld
	$(LD) -T module.ld -o $@ $(OUT)/power_control.o $(OUT)/power_control_adapter.o

test: $(OUT)/device_configure.elf $(OUT)/power_control_test.elf
	$(PYTHON) verify_device_configure.py --elf $< --output $(OUT)/device-configure-differential.json
	$(PYTHON) verify_power_control.py --elf $(OUT)/power_control_test.elf --output $(OUT)/power-control-differential.json
