CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CPU ?= cortex-m4
OUT ?= ../../../build/bootloader-completion/manager-task
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -Wall -Wextra -Werror
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c manager_task.c -o $(OUT)/manager_task.o
	$(LD) -T module.ld -o $(OUT)/manager-task.elf $(OUT)/manager_task.o
verify: all
	$(PYTHON) verify.py --elf $(OUT)/manager-task.elf --output $(OUT)/comparison.json

sender-integrated:
	mkdir -p ../../../build/bootloader-completion/manager-sender-integrated
	$(CC) $(CFLAGS) -c manager_task.c -o ../../../build/bootloader-completion/manager-sender-integrated/manager_task.o
	$(CC) $(CFLAGS) -c ../dfu_task/context.c -o ../../../build/bootloader-completion/manager-sender-integrated/context.o
	$(LD) -T sender_integrated.ld -o ../../../build/bootloader-completion/manager-sender-integrated/manager-sender.elf ../../../build/bootloader-completion/manager-sender-integrated/manager_task.o ../../../build/bootloader-completion/manager-sender-integrated/context.o
	$(PYTHON) verify_sender_integrated.py --elf ../../../build/bootloader-completion/manager-sender-integrated/manager-sender.elf --output ../../../build/bootloader-completion/manager-sender-integrated/comparison.json

setup-compatible:
	mkdir -p ../../../build/bootloader-completion/manager-setup-compatible
	$(CC) $(CFLAGS) -c manager_setup.c -o ../../../build/bootloader-completion/manager-setup-compatible/manager_setup.o
	$(CC) $(CFLAGS) -c ../thread_creation/thread_priority.c -o ../../../build/bootloader-completion/manager-setup-compatible/thread_priority.o
	$(CC) $(CFLAGS) -c ../thread_creation/kernel_runtime.c -o ../../../build/bootloader-completion/manager-setup-compatible/kernel_runtime.o
	$(CC) $(CFLAGS) -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/manager-setup-compatible/runtime_mode.o
	$(LD) -T setup_module.ld -o ../../../build/bootloader-completion/manager-setup-compatible/manager-setup.elf ../../../build/bootloader-completion/manager-setup-compatible/*.o
	$(PYTHON) verify_setup.py --elf ../../../build/bootloader-completion/manager-setup-compatible/manager-setup.elf --output ../../../build/bootloader-completion/manager-setup-compatible/comparison.json

event-compatible:
	mkdir -p ../../../build/bootloader-completion/manager-event-compatible
	$(CC) $(CFLAGS) -c event_runtime.c -o ../../../build/bootloader-completion/manager-event-compatible/event_runtime.o
	$(LD) -T event_module.ld -o ../../../build/bootloader-completion/manager-event-compatible/event-runtime.elf ../../../build/bootloader-completion/manager-event-compatible/event_runtime.o
	$(PYTHON) verify_event.py --elf ../../../build/bootloader-completion/manager-event-compatible/event-runtime.elf --output ../../../build/bootloader-completion/manager-event-compatible/comparison.json

dispatch-compatible:
	mkdir -p ../../../build/bootloader-completion/manager-dispatch-compatible
	$(CC) $(CFLAGS) -c event_dispatch.c -o ../../../build/bootloader-completion/manager-dispatch-compatible/event_dispatch.o
	$(CC) $(CFLAGS) -c ../thread_creation/kernel_runtime.c -o ../../../build/bootloader-completion/manager-dispatch-compatible/kernel_runtime.o
	$(CC) $(CFLAGS) -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/manager-dispatch-compatible/runtime_mode.o
	$(LD) -T dispatch_module.ld -o ../../../build/bootloader-completion/manager-dispatch-compatible/event-dispatch.elf ../../../build/bootloader-completion/manager-dispatch-compatible/*.o
	$(PYTHON) verify_dispatch.py --elf ../../../build/bootloader-completion/manager-dispatch-compatible/event-dispatch.elf --output ../../../build/bootloader-completion/manager-dispatch-compatible/comparison.json
