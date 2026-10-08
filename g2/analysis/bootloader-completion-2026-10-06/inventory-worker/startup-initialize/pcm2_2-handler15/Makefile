CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
BASE_ELF ?= /tmp/opencfw-root-pcm22/final-candidate.elf
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O1 -Wall -Wextra
.PHONY: all verify
all: handler15-addon.elf
handler15.o: handler15.c
	$(CLANG) $(CFLAGS) -c $< -o $@
handler15-addon.elf: handler15.o module.ld $(BASE_ELF)
	$(LD) -T module.ld --build-id=none --just-symbols=$(BASE_ELF) -Map=handler15-addon.map -o $@ handler15.o
verify: handler15-addon.elf
	$(PYTHON) verify.py --base $(BASE_ELF) --addon handler15-addon.elf --output comparison.json
