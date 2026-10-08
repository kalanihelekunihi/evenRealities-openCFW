CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
BASE_ELF ?= /tmp/opencfw-root-pcm22-relocated/record-candidate.elf
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O1 -Wall -Wextra
.PHONY: all verify clean
all: handler3-addon.elf
handler3.o: handler3.c
	$(CLANG) $(CFLAGS) -c $< -o $@
handler3-addon.elf: handler3.o module.ld $(BASE_ELF)
	$(LD) -z max-page-size=0x100 -T module.ld --build-id=none --just-symbols=$(BASE_ELF) -Map=handler3-addon.map -o $@ handler3.o
verify: handler3-addon.elf
	$(PYTHON) verify.py --base $(BASE_ELF) --addon handler3-addon.elf --output comparison.json
	$(PYTHON) verify_natural.py --base $(BASE_ELF) --addon handler3-addon.elf --output comparison-natural.json
clean:
	rm -f handler3.o handler3-addon.elf handler3-addon.map
