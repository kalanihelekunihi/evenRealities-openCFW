CLANG ?= clang
LD = /opt/homebrew/bin/arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS = --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard \
	-ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O1 -Wall -Wextra
CLOCK_DIR = ../../../../components/bootloader/clock_manager
CLOCK_OBJS = clock_manager_native.o clock_classes_native.o clock2_native.o \
	clock4_native.o clock5_native.o clock6_native.o

.PHONY: all verify clean
all: event.elf

event.elf: native_event.c test_event_providers.c children_native.c ../../../../components/bootloader/platform_control/critical_save.S native.ld $(CLOCK_OBJS)
	$(CLANG) $(CFLAGS) -c native_event.c -o native_event.o
	$(CLANG) $(CFLAGS) -c test_event_providers.c -o test_event_providers.o
	$(CLANG) $(CFLAGS) -c children_native.c -o children_native.o
	$(MAKE) $(CLOCK_OBJS)
	$(CLANG) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -c \
		../../../../components/bootloader/platform_control/critical_save.S -o critical_save.o
	$(LD) -T native.ld --build-id=none -Map=event.map -o $@ \
		native_event.o test_event_providers.o children_native.o critical_save.o $(CLOCK_OBJS)

event-cuts.elf: native_event.c test_event_providers.c children_native.c ../../../../components/bootloader/platform_control/critical_save.S native.ld $(CLOCK_OBJS)
	$(CLANG) $(CFLAGS) -c native_event.c -o native_event.o
	$(CLANG) $(CFLAGS) -DEVENT_CHILD_CUTS -c test_event_providers.c -o test_event_providers.o
	$(CLANG) $(CFLAGS) -c children_native.c -o children_native.o
	$(MAKE) $(CLOCK_OBJS)
	$(CLANG) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=hard -c \
		../../../../components/bootloader/platform_control/critical_save.S -o critical_save.o
	$(LD) -T native.ld --build-id=none -Map=event-cuts.map -o $@ \
		native_event.o test_event_providers.o children_native.o critical_save.o $(CLOCK_OBJS)

clock_manager_native.o: $(CLOCK_DIR)/clock_manager.c
	$(CLANG) $(CFLAGS) -I$(CLOCK_DIR) -c $< -o $@
clock_classes_native.o: $(CLOCK_DIR)/clock_class_providers.c
	$(CLANG) $(CFLAGS) -I$(CLOCK_DIR) -c $< -o $@
clock2_native.o: $(CLOCK_DIR)/clock_class_provider2.c
	$(CLANG) $(CFLAGS) -I$(CLOCK_DIR) -c $< -o $@
clock4_native.o: $(CLOCK_DIR)/clock_class_provider4.c
	$(CLANG) $(CFLAGS) -I$(CLOCK_DIR) -c $< -o $@
clock5_native.o: $(CLOCK_DIR)/clock_class_provider5.c
	$(CLANG) $(CFLAGS) -I$(CLOCK_DIR) -c $< -o $@
clock6_native.o: $(CLOCK_DIR)/clock_class_provider6.c
	$(CLANG) $(CFLAGS) -I$(CLOCK_DIR) -c $< -o $@

child-native.elf: children_native.c native_child.ld $(CLOCK_OBJS)
	$(CLANG) $(CFLAGS) -c children_native.c -o children_native.o
	$(LD) -T native_child.ld --build-id=none -Map=child-native.map -o $@ children_native.o $(CLOCK_OBJS)

verify: event.elf child-native.elf
	$(PYTHON) verify_evidence.py
	$(PYTHON) compare_children.py --elf child-native.elf --output child-comparison-transition.json
	$(PYTHON) compare_transition.py --elf child-native.elf --output transition-comparison-corrected.json
	$(PYTHON) compare_native.py --elf event.elf --output comparison-native-transition.json
	$(MAKE) event-cuts.elf
	$(PYTHON) compare_native.py --elf event-cuts.elf --child-cuts --output comparison-wrapper-cuts-transition.json

clean:
	rm -f event.elf event.map event-cuts.elf event-cuts.map native_event.o test_event_providers.o children_native.o critical_save.o $(CLOCK_OBJS) comparison.failure.json comparison-native-decoder.json comparison-wrapper-cuts-current.json child-comparison-decoder.json child-native.elf child-native.map
