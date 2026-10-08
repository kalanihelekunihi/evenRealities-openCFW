CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard \
	-ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O1 -Wall -Wextra
CLOCK = ../../../../../components/bootloader/clock_manager
PLATFORM = ../../../../../components/bootloader/platform_control
POLL = ../../../../../components/bootloader/nor_mspi_init/status_poll.c

.PHONY: all verify
all: handlers.elf

handlers.o: handlers.c
	$(CLANG) $(CFLAGS) -c $< -o $@

timer_support.o: ../pcm2_2-native/timer_support.c
	$(CLANG) $(CFLAGS) -c $< -o $@

critical_save.o: $(PLATFORM)/critical_save.S
	$(CLANG) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -c $< -o $@

status_poll.o: $(POLL)
	$(CLANG) $(CFLAGS) -c $< -o $@

clock_manager.o: $(CLOCK)/clock_manager.c
	$(CLANG) $(CFLAGS) -I$(CLOCK) -c $< -o $@
clock_classes.o: $(CLOCK)/clock_class_providers.c
	$(CLANG) $(CFLAGS) -I$(CLOCK) -c $< -o $@
clock2.o: $(CLOCK)/clock_class_provider2.c
	$(CLANG) $(CFLAGS) -I$(CLOCK) -c $< -o $@
clock4.o: $(CLOCK)/clock_class_provider4.c
	$(CLANG) $(CFLAGS) -I$(CLOCK) -c $< -o $@
clock5.o: $(CLOCK)/clock_class_provider5.c
	$(CLANG) $(CFLAGS) -I$(CLOCK) -c $< -o $@
clock6.o: $(CLOCK)/clock_class_provider6.c
	$(CLANG) $(CFLAGS) -I$(CLOCK) -c $< -o $@

handlers.elf: handlers.o timer_support.o critical_save.o status_poll.o \
	clock_manager.o clock_classes.o clock2.o clock4.o clock5.o clock6.o module.ld
	$(LD) -T module.ld --build-id=none -Map=handlers.map -o $@ \
		handlers.o timer_support.o critical_save.o status_poll.o \
		clock_manager.o clock_classes.o clock2.o clock4.o clock5.o clock6.o

verify: handlers.elf
	$(PYTHON) verify.py --elf handlers.elf --output comparison.json
