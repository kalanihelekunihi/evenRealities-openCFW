CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
BASE_ELF ?= /tmp/opencfw-root-pcm22-relocated/record-candidate.elf
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O1 -Wall -Wextra
.PHONY: all verify
all: handler17-addon.elf
handler17.o: handler17.c
	$(CLANG) $(CFLAGS) -c $< -o $@
handler17-addon.elf: handler17.o module.ld $(BASE_ELF)
	$(LD) --gc-sections -T module.ld --build-id=none --just-symbols=$(BASE_ELF) -Map=handler17-addon.map -o $@ handler17.o
verify: handler17-addon.elf
	$(PYTHON) verify17.py --base $(BASE_ELF) --addon handler17-addon.elf --output comparison.json
