CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
BASE_ELF ?= /tmp/opencfw-root-pcm22-relocated/candidate.elf
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O1 -Wall -Wextra
.PHONY: all verify
all: handler16-addon.elf
handler16.o: handler16.c
	$(CLANG) $(CFLAGS) -c $< -o $@
event_a_transitions.o: ../../startup-events-a/startup_event_a_transitions.c
	$(CLANG) $(CFLAGS) -c $< -o $@
walker16.o: walker16.c
	$(CLANG) $(CFLAGS) -c $< -o $@
handler16-addon.elf: handler16.o event_a_transitions.o walker16.o module.ld $(BASE_ELF)
	$(LD) -T module.ld --build-id=none --just-symbols=$(BASE_ELF) -Map=handler16-addon.map -o $@ handler16.o event_a_transitions.o walker16.o
verify:
	$(PYTHON) verify.py --elf $(BASE_ELF) --output comparison-relocated-direct.json
	$(PYTHON) verify_callchain.py --elf $(BASE_ELF) --output comparison-walker-selector16-relocated.json
