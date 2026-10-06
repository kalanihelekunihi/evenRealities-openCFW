OUT ?= out
CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-fshort-enums -std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all test chain-test chain-table-test clean
all: $(OUT)/cmdq_consumer.elf

$(OUT):
	mkdir -p $@

$(OUT)/cmdq.o: am_hal_cmdq_init.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/cmdq_consumer.elf: $(OUT)/cmdq.o module.ld
	$(LD) -T module.ld -o $@ $(OUT)/cmdq.o

$(OUT)/enable.o: ../mspi-enable/am_hal_mspi_enable.c | $(OUT)
	$(CC) $(CFLAGS) -I../../../../components/foundation/ambiq_mspi -c $< -o $@

$(OUT)/cq_init.o: ../mspi-cq-init/mspi_cq_init.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/chain_adapter.o: chain_adapter.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/mspi_chain.elf: $(OUT)/enable.o $(OUT)/cq_init.o $(OUT)/cmdq.o $(OUT)/chain_adapter.o chain.ld
	$(LD) -T chain.ld -o $@ $(OUT)/enable.o $(OUT)/cq_init.o $(OUT)/cmdq.o $(OUT)/chain_adapter.o

$(OUT)/cmdq_ops_table.o: cmdq_ops_table.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/mspi_chain_with_ops.elf: $(OUT)/enable.o $(OUT)/cq_init.o $(OUT)/cmdq.o $(OUT)/chain_adapter.o $(OUT)/cmdq_ops_table.o chain_with_ops.ld
	$(LD) -T chain_with_ops.ld -o $@ $(OUT)/enable.o $(OUT)/cq_init.o $(OUT)/cmdq.o $(OUT)/chain_adapter.o $(OUT)/cmdq_ops_table.o

test: $(OUT)/cmdq_consumer.elf
	$(PYTHON) verify_cmdq.py --elf $< --output $(OUT)/comparison.json

chain-test: $(OUT)/mspi_chain.elf
	$(PYTHON) verify_chain.py --elf $< --output $(OUT)/chain-comparison.json

chain-table-test: $(OUT)/mspi_chain_with_ops.elf
	$(PYTHON) verify_chain.py --source-table --elf $< --output $(OUT)/chain-table-comparison.json

clean:
	rm -rf $(OUT)
