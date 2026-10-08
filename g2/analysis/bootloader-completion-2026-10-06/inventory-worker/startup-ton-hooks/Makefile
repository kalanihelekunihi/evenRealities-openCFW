PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CLANG ?= clang
ARM_LD ?= arm-none-eabi-ld

.PHONY: test clean
test: ton_hooks.elf
	$(PYTHON) verify.py --elf ton_hooks.elf --output result.json

ton_hooks.o: ton_hooks.c ton_hooks.h
	$(CLANG) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -O2 -ffreestanding -fno-builtin -fno-unwind-tables -fno-asynchronous-unwind-tables -c $< -o $@

ton_hooks.elf: ton_hooks.o module.ld
	$(ARM_LD) -T module.ld -o $@ ton_hooks.o

clean:
	rm -f ton_hooks.o ton_hooks.elf result.json result.failure.json
