ROOT := ../../../../..
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
OUT ?= /tmp/opencfw-uart-rx
FLAGS := --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft -O0 -ffreestanding -fno-builtin
all:
	clang $(FLAGS) -c $(ROOT)/g2/components/bootloader/initializer_callbacks/uart_rx.c -o $(OUT).o
	clang $(FLAGS) -ffunction-sections -fdata-sections -c $(ROOT)/g2/components/bootloader/initializer_callbacks/elog_uart_tx.c -o $(OUT)-ring.o
	arm-none-eabi-ld --gc-sections --undefined=opencfw_boot_uart_rx_claim --undefined=opencfw_boot_uart_rx_cancel --undefined=opencfw_boot_uart_rx_fifo --undefined=opencfw_boot_uart_rx_collect --undefined=opencfw_boot_uart_rx_pump --undefined=opencfw_boot_uart_rx_start --undefined=opencfw_boot_uart_rx_blocking -T module.ld $(OUT).o $(OUT)-ring.o -o $(OUT).elf
verify: all
	$(PYTHON) verify.py --elf $(OUT).elf --output comparison.json
