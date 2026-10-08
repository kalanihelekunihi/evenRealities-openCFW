CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard \
	-ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O0 -Wall -Wextra

.PHONY: all verify verify-transitions
all: event_a.elf

event_a.elf: startup_events_a.c startup_event_a_trim.c startup_events_a.h test_event_a_providers.c native.ld ../../../../components/bootloader/platform_control/critical_save.S
	$(CLANG) $(CFLAGS) -c startup_events_a.c -o startup_events_a.o
	$(CLANG) $(CFLAGS) -c startup_event_a_trim.c -o startup_event_a_trim.o
	$(CLANG) $(CFLAGS) -c test_event_a_providers.c -o test_event_a_providers.o
	$(CLANG) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -c ../../../../components/bootloader/platform_control/critical_save.S -o critical_save.o
	$(LD) -T native.ld --build-id=none -Map=event_a.map -o $@ startup_events_a.o startup_event_a_trim.o test_event_a_providers.o critical_save.o

event_a_transitions.elf: startup_event_a_transitions.c startup_event_a_sequence8.c startup_event_a_trim.c native.ld
	$(CLANG) $(CFLAGS) -c startup_event_a_transitions.c -o startup_event_a_transitions.o
	$(CLANG) $(CFLAGS) -c startup_event_a_sequence8.c -o startup_event_a_sequence8.o
	$(CLANG) $(CFLAGS) -c startup_event_a_trim.c -o startup_event_a_trim.transitions.o
	$(LD) -T native.ld --entry=event_a_state_transition_sequence --build-id=none -Map=event_a_transitions.map -o $@ startup_event_a_transitions.o startup_event_a_sequence8.o startup_event_a_trim.transitions.o

event_a_native.elf: startup_events_a.c startup_event_a_trim.c startup_event_a_transitions.c startup_event_a_sequence8.c startup_events_a.h native.ld ../../../../components/bootloader/platform_control/critical_save.S
	$(CLANG) $(CFLAGS) -c startup_events_a.c -o startup_events_a.native.o
	$(CLANG) $(CFLAGS) -c startup_event_a_trim.c -o startup_event_a_trim.native.o
	$(CLANG) $(CFLAGS) -c startup_event_a_transitions.c -o startup_event_a_transitions.native.o
	$(CLANG) $(CFLAGS) -c startup_event_a_sequence8.c -o startup_event_a_sequence8.native.o
	$(CLANG) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -c ../../../../components/bootloader/platform_control/critical_save.S -o critical_save.native.o
	$(LD) -T native.ld --build-id=none -Map=event_a_native.map -o $@ startup_events_a.native.o startup_event_a_trim.native.o startup_event_a_transitions.native.o startup_event_a_sequence8.native.o critical_save.native.o

verify: event_a.elf
	$(PYTHON) verify_event_a.py --elf event_a.elf --output comparison.json

verify-transitions: event_a_transitions.elf
	$(PYTHON) verify_event_a_transitions.py --elf event_a_transitions.elf --output comparison-transitions.json

verify-native: event_a_native.elf
	$(PYTHON) verify_event_a_native.py --elf event_a_native.elf --output comparison-native.json
