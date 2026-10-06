COMPONENT := ../../../../components/bootloader/thread_creation
OUT ?= out
CC := clang
LD := arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CFLAGS := --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft \
	-ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
	-std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all test
all: $(OUT)/event_waiter_wake.elf

$(OUT):
	mkdir -p $@

$(OUT)/event_waiter_wake.o: $(COMPONENT)/event_waiter_wake.c $(COMPONENT)/event_waiter_wake.h $(COMPONENT)/timer_wait.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENT) -c $< -o $@

$(OUT)/timer_wait.o: $(COMPONENT)/timer_wait.c $(COMPONENT)/timer_wait.h | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENT) -c $< -o $@

$(OUT)/scheduler_resume.o: $(COMPONENT)/scheduler_resume.c | $(OUT)
	$(CC) $(CFLAGS) -I$(COMPONENT) -c $< -o $@

$(OUT)/event_waiter_wake.elf: $(OUT)/event_waiter_wake.o $(OUT)/timer_wait.o $(OUT)/scheduler_resume.o event_waiter_wake_test.ld
	$(LD) --gc-sections -u opencfw_bl_missed_yield -T event_waiter_wake_test.ld -o $@ $(OUT)/event_waiter_wake.o $(OUT)/timer_wait.o $(OUT)/scheduler_resume.o

test: $(OUT)/event_waiter_wake.elf
	$(PYTHON) verify_event_waiter_wake.py --elf $< --output $(OUT)/comparison.json
