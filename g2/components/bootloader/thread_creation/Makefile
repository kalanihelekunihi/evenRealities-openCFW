CC = clang
LD = arm-none-eabi-ld
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
CPU ?= cortex-m55
OUT ?= ../../../build/bootloader-completion/thread-creation
CFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -Wall -Wextra -Werror
all:
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) -c thread_creation.c -o $(OUT)/thread_creation.o
	$(LD) -T module.ld -o $(OUT)/thread-creation.elf $(OUT)/thread_creation.o
verify-compatible:
	$(MAKE) all CPU=cortex-m4 OUT=../../../build/bootloader-completion/thread-creation-compatible
	$(PYTHON) verify.py --elf ../../../build/bootloader-completion/thread-creation-compatible/thread-creation.elf --output ../../../build/bootloader-completion/thread-creation-compatible/comparison-first.json

integrated-compatible:
	$(MAKE) -C ../main_callback startup-integrated-compatible
	mkdir -p ../../../build/bootloader-completion/thread-creation-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_creation.c -o ../../../build/bootloader-completion/thread-creation-startup-compatible/thread_creation.o
	$(LD) -T startup_thread_integrated.ld -o ../../../build/bootloader-completion/thread-creation-startup-compatible/startup-thread.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-creation-startup-compatible/thread_creation.o
	$(PYTHON) verify_integrated.py --elf ../../../build/bootloader-completion/thread-creation-startup-compatible/startup-thread.elf --output ../../../build/bootloader-completion/thread-creation-startup-compatible/comparison-first.json

static-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-static-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_creation.c -o ../../../build/bootloader-completion/thread-static-compatible/thread_creation.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_static.c -o ../../../build/bootloader-completion/thread-static-compatible/kernel_static.o
	$(LD) -T static_module.ld -o ../../../build/bootloader-completion/thread-static-compatible/thread-static.elf ../../../build/bootloader-completion/thread-static-compatible/thread_creation.o ../../../build/bootloader-completion/thread-static-compatible/kernel_static.o
	$(PYTHON) verify_static.py --elf ../../../build/bootloader-completion/thread-static-compatible/thread-static.elf --output ../../../build/bootloader-completion/thread-static-compatible/comparison-first.json

register-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-register-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_creation.c -o ../../../build/bootloader-completion/thread-register-compatible/thread_creation.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_static.c -o ../../../build/bootloader-completion/thread-register-compatible/kernel_static.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_register.c -o ../../../build/bootloader-completion/thread-register-compatible/thread_register.o
	$(LD) -T register_module.ld -o ../../../build/bootloader-completion/thread-register-compatible/thread-register.elf ../../../build/bootloader-completion/thread-register-compatible/*.o
	$(PYTHON) verify_register.py --elf ../../../build/bootloader-completion/thread-register-compatible/thread-register.elf --output ../../../build/bootloader-completion/thread-register-compatible/comparison-first.json

runtime-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-runtime-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_creation.c -o ../../../build/bootloader-completion/thread-runtime-compatible/thread_creation.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_static.c -o ../../../build/bootloader-completion/thread-runtime-compatible/kernel_static.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_register.c -o ../../../build/bootloader-completion/thread-runtime-compatible/thread_register.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_runtime.c -o ../../../build/bootloader-completion/thread-runtime-compatible/kernel_runtime.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-runtime-compatible/runtime_mode.o
	$(LD) -T runtime_module.ld -o ../../../build/bootloader-completion/thread-runtime-compatible/thread-runtime.elf ../../../build/bootloader-completion/thread-runtime-compatible/*.o
	$(PYTHON) verify_runtime.py --elf ../../../build/bootloader-completion/thread-runtime-compatible/thread-runtime.elf --output ../../../build/bootloader-completion/thread-runtime-compatible/comparison-first.json

runtime-integrated-compatible:
	$(MAKE) -C ../main_callback startup-integrated-compatible
	$(MAKE) runtime-compatible
	mkdir -p ../../../build/bootloader-completion/thread-runtime-startup-compatible
	$(LD) -T startup_runtime_integrated.ld -o ../../../build/bootloader-completion/thread-runtime-startup-compatible/startup-runtime.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o
	$(PYTHON) verify_runtime_integrated.py --elf ../../../build/bootloader-completion/thread-runtime-startup-compatible/startup-runtime.elf --output ../../../build/bootloader-completion/thread-runtime-startup-compatible/comparison-first.json

lifecycle-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-lifecycle-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -ffunction-sections -c lifecycle.c -o ../../../build/bootloader-completion/thread-lifecycle-compatible/lifecycle.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -ffunction-sections -c kernel_runtime.c -o ../../../build/bootloader-completion/thread-lifecycle-compatible/kernel_runtime.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -ffunction-sections -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-lifecycle-compatible/runtime_mode.o
	$(LD) -T lifecycle_module.ld -o ../../../build/bootloader-completion/thread-lifecycle-compatible/lifecycle.elf ../../../build/bootloader-completion/thread-lifecycle-compatible/*.o
	$(PYTHON) verify_lifecycle.py --elf ../../../build/bootloader-completion/thread-lifecycle-compatible/lifecycle.elf --output ../../../build/bootloader-completion/thread-lifecycle-compatible/comparison-first.json

bootstrap-compatible:
	$(MAKE) runtime-compatible
	mkdir -p ../../../build/bootloader-completion/thread-bootstrap-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c scheduler_bootstrap.c -o ../../../build/bootloader-completion/thread-bootstrap-compatible/scheduler_bootstrap.o
	$(LD) -T bootstrap_module.ld -o ../../../build/bootloader-completion/thread-bootstrap-compatible/bootstrap.elf ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-bootstrap-compatible/scheduler_bootstrap.o
	$(PYTHON) verify_bootstrap.py --elf ../../../build/bootloader-completion/thread-bootstrap-compatible/bootstrap.elf --output ../../../build/bootloader-completion/thread-bootstrap-compatible/comparison-first.json

bootstrap-integrated-compatible:
	$(MAKE) -C ../main_callback startup-integrated-compatible
	$(MAKE) bootstrap-compatible
	mkdir -p ../../../build/bootloader-completion/thread-bootstrap-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c lifecycle.c -o ../../../build/bootloader-completion/thread-bootstrap-startup-compatible/lifecycle.o
	$(LD) -T startup_bootstrap_integrated.ld -o ../../../build/bootloader-completion/thread-bootstrap-startup-compatible/startup-bootstrap.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-bootstrap-compatible/scheduler_bootstrap.o ../../../build/bootloader-completion/thread-bootstrap-startup-compatible/lifecycle.o
	$(PYTHON) verify_bootstrap_integrated.py --elf ../../../build/bootloader-completion/thread-bootstrap-startup-compatible/startup-bootstrap.elf --output ../../../build/bootloader-completion/thread-bootstrap-startup-compatible/comparison-first.json

source-m55:
	mkdir -p ../../../build/bootloader-completion/thread-source-m55
	$(CC) $(CFLAGS) -c thread_creation.c -o ../../../build/bootloader-completion/thread-source-m55/thread_creation.o
	$(CC) $(CFLAGS) -c kernel_static.c -o ../../../build/bootloader-completion/thread-source-m55/kernel_static.o
	$(CC) $(CFLAGS) -c thread_register.c -o ../../../build/bootloader-completion/thread-source-m55/thread_register.o
	$(CC) $(CFLAGS) -c kernel_runtime.c -o ../../../build/bootloader-completion/thread-source-m55/kernel_runtime.o
	$(CC) $(CFLAGS) -c lifecycle.c -o ../../../build/bootloader-completion/thread-source-m55/lifecycle.o
	$(CC) $(CFLAGS) -c scheduler_bootstrap.c -o ../../../build/bootloader-completion/thread-source-m55/scheduler_bootstrap.o

timer-compatible:
	$(MAKE) runtime-compatible
	mkdir -p ../../../build/bootloader-completion/thread-timer-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c scheduler_bootstrap.c -o ../../../build/bootloader-completion/thread-timer-compatible/scheduler_bootstrap.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c timer_service.c -o ../../../build/bootloader-completion/thread-timer-compatible/timer_service.o
	$(LD) -T timer_module.ld -o ../../../build/bootloader-completion/thread-timer-compatible/timer.elf ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-timer-compatible/*.o
	$(PYTHON) verify_timer.py --elf ../../../build/bootloader-completion/thread-timer-compatible/timer.elf --output ../../../build/bootloader-completion/thread-timer-compatible/comparison-first.json

select-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-select-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_select.c -o ../../../build/bootloader-completion/thread-select-compatible/thread_select.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_runtime.c -o ../../../build/bootloader-completion/thread-select-compatible/kernel_runtime.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-select-compatible/runtime_mode.o
	$(LD) -T select_module.ld -o ../../../build/bootloader-completion/thread-select-compatible/select.elf ../../../build/bootloader-completion/thread-select-compatible/*.o
	$(PYTHON) verify_select.py --elf ../../../build/bootloader-completion/thread-select-compatible/select.elf --output ../../../build/bootloader-completion/thread-select-compatible/comparison-first.json

port-compatible:
	$(MAKE) runtime-compatible
	mkdir -p ../../../build/bootloader-completion/thread-port-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c scheduler_bootstrap.c -o ../../../build/bootloader-completion/thread-port-compatible/scheduler_bootstrap.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c timer_service.c -o ../../../build/bootloader-completion/thread-port-compatible/timer_service.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_select.c -o ../../../build/bootloader-completion/thread-port-compatible/thread_select.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c port_start.c -o ../../../build/bootloader-completion/thread-port-compatible/port_start.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c first_task_transfer.S -o ../../../build/bootloader-completion/thread-port-compatible/first_task_transfer.o
	$(LD) -T port_module.ld -o ../../../build/bootloader-completion/thread-port-compatible/port.elf ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o
	$(PYTHON) verify_port.py --elf ../../../build/bootloader-completion/thread-port-compatible/port.elf --output ../../../build/bootloader-completion/thread-port-compatible/comparison-first.json

port-integrated-compatible:
	$(MAKE) -C ../main_callback startup-integrated-compatible
	$(MAKE) port-compatible
	mkdir -p ../../../build/bootloader-completion/thread-port-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c lifecycle.c -o ../../../build/bootloader-completion/thread-port-startup-compatible/lifecycle.o
	$(LD) -T startup_port_integrated.ld -o ../../../build/bootloader-completion/thread-port-startup-compatible/startup-port.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/thread-port-startup-compatible/lifecycle.o
	$(PYTHON) verify_port_integrated.py --elf ../../../build/bootloader-completion/thread-port-startup-compatible/startup-port.elf --output ../../../build/bootloader-completion/thread-port-startup-compatible/comparison-first.json

pendsv-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-pendsv-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c thread_select.c -o ../../../build/bootloader-completion/thread-pendsv-compatible/thread_select.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c kernel_runtime.c -o ../../../build/bootloader-completion/thread-pendsv-compatible/kernel_runtime.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-pendsv-compatible/runtime_mode.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c exception_entry.S -o ../../../build/bootloader-completion/thread-pendsv-compatible/exception_entry.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -c restore_probe.S -o ../../../build/bootloader-completion/thread-pendsv-compatible/restore_probe.o
	$(LD) -T pendsv_module.ld -o ../../../build/bootloader-completion/thread-pendsv-compatible/pendsv.elf ../../../build/bootloader-completion/thread-pendsv-compatible/*.o
	$(PYTHON) verify_pendsv.py --elf ../../../build/bootloader-completion/thread-pendsv-compatible/pendsv.elf --output ../../../build/bootloader-completion/thread-pendsv-compatible/comparison-first.json

dynamic-compatible:
	$(MAKE) runtime-compatible
	mkdir -p ../../../build/bootloader-completion/thread-dynamic-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_dynamic.c -o ../../../build/bootloader-completion/thread-dynamic-compatible/kernel_dynamic.o
	$(LD) -T dynamic_module.ld -o ../../../build/bootloader-completion/thread-dynamic-compatible/dynamic.elf ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-dynamic-compatible/kernel_dynamic.o
	$(PYTHON) verify_dynamic.py --elf ../../../build/bootloader-completion/thread-dynamic-compatible/dynamic.elf --output ../../../build/bootloader-completion/thread-dynamic-compatible/comparison-first.json

heap-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-heap-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c rtos_heap.c -o ../../../build/bootloader-completion/thread-heap-compatible/rtos_heap.o
	$(LD) -T heap_module.ld -o ../../../build/bootloader-completion/thread-heap-compatible/heap.elf ../../../build/bootloader-completion/thread-heap-compatible/rtos_heap.o
	$(PYTHON) verify_heap.py --elf ../../../build/bootloader-completion/thread-heap-compatible/heap.elf --output ../../../build/bootloader-completion/thread-heap-compatible/comparison-first.json

owned-heap-compatible:
	$(MAKE) runtime-compatible
	mkdir -p ../../../build/bootloader-completion/thread-owned-heap-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_dynamic.c -o ../../../build/bootloader-completion/thread-owned-heap-compatible/kernel_dynamic.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c rtos_heap.c -o ../../../build/bootloader-completion/thread-owned-heap-compatible/rtos_heap.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c scheduler_resume.c -o ../../../build/bootloader-completion/thread-owned-heap-compatible/scheduler_resume.o
	$(LD) -T owned_heap_module.ld -o ../../../build/bootloader-completion/thread-owned-heap-compatible/owned-heap.elf ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-owned-heap-compatible/*.o
	$(PYTHON) verify_owned_heap.py --elf ../../../build/bootloader-completion/thread-owned-heap-compatible/owned-heap.elf --output ../../../build/bootloader-completion/thread-owned-heap-compatible/comparison-first.json

tick-compatible:
	$(MAKE) runtime-compatible
	mkdir -p ../../../build/bootloader-completion/thread-tick-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_dynamic.c -o ../../../build/bootloader-completion/thread-tick-compatible/kernel_dynamic.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c rtos_heap.c -o ../../../build/bootloader-completion/thread-tick-compatible/rtos_heap.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c scheduler_resume.c -o ../../../build/bootloader-completion/thread-tick-compatible/scheduler_resume.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c scheduler_tick.c -o ../../../build/bootloader-completion/thread-tick-compatible/scheduler_tick.o
	$(LD) -T tick_module.ld -o ../../../build/bootloader-completion/thread-tick-compatible/tick.elf ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-tick-compatible/*.o
	$(PYTHON) verify_tick.py --elf ../../../build/bootloader-completion/thread-tick-compatible/tick.elf --output ../../../build/bootloader-completion/thread-tick-compatible/comparison-first.json

source-m55-all: source-m55
	$(CC) $(CFLAGS) -c thread_priority.c -o ../../../build/bootloader-completion/thread-source-m55/thread_priority.o
	$(CC) $(CFLAGS) -c kernel_dynamic.c -o ../../../build/bootloader-completion/thread-source-m55/kernel_dynamic.o
	$(CC) $(CFLAGS) -c timer_service.c -o ../../../build/bootloader-completion/thread-source-m55/timer_service.o
	$(CC) $(CFLAGS) -c port_start.c -o ../../../build/bootloader-completion/thread-source-m55/port_start.o
	$(CC) $(CFLAGS) -c thread_select.c -o ../../../build/bootloader-completion/thread-source-m55/thread_select.o
	$(CC) $(CFLAGS) -c rtos_heap.c -o ../../../build/bootloader-completion/thread-source-m55/rtos_heap.o
	$(CC) $(CFLAGS) -c scheduler_resume.c -o ../../../build/bootloader-completion/thread-source-m55/scheduler_resume.o
	$(CC) $(CFLAGS) -c scheduler_tick.c -o ../../../build/bootloader-completion/thread-source-m55/scheduler_tick.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c exception_entry.S -o ../../../build/bootloader-completion/thread-source-m55/exception_entry.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -c first_task_transfer.S -o ../../../build/bootloader-completion/thread-source-m55/first_task_transfer.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -c restore_probe.S -o ../../../build/bootloader-completion/thread-source-m55/restore_probe.o

allocator-integrated-compatible:
	$(MAKE) -C ../main_callback startup-integrated-compatible
	$(MAKE) port-compatible
	$(MAKE) -C ../allocator all CPU=cortex-m4 OUT=../../../build/bootloader-completion/allocator-compatible
	mkdir -p ../../../build/bootloader-completion/thread-allocator-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c lifecycle.c -o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o
	$(LD) -T startup_allocator_integrated.ld -o ../../../build/bootloader-completion/thread-allocator-startup-compatible/startup-allocator.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o
	$(PYTHON) verify_allocator_integrated.py --elf ../../../build/bootloader-completion/thread-allocator-startup-compatible/startup-allocator.elf --output ../../../build/bootloader-completion/thread-allocator-startup-compatible/comparison-first.json

timer-integrated-compatible: startup-provider-objects
	mkdir -p ../../../build/bootloader-completion/thread-timer-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../port_timer/port_timer.c -o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o
	$(LD) -T startup_timer_integrated.ld -o ../../../build/bootloader-completion/thread-timer-startup-compatible/startup-timer.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o
	$(PYTHON) verify_timer_integrated.py --elf ../../../build/bootloader-completion/thread-timer-startup-compatible/startup-timer.elf --output ../../../build/bootloader-completion/thread-timer-startup-compatible/comparison-first.json

nor-integrated-compatible: startup-provider-objects
	$(MAKE) -C ../nor_init all
	mkdir -p ../../../build/bootloader-completion/thread-nor-startup-compatible
	$(LD) -T startup_nor_integrated.ld -o ../../../build/bootloader-completion/thread-nor-startup-compatible/startup-nor.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o
	$(PYTHON) verify_nor_integrated.py --elf ../../../build/bootloader-completion/thread-nor-startup-compatible/startup-nor.elf --output ../../../build/bootloader-completion/thread-nor-startup-compatible/comparison-first.json

clock-integrated-compatible: startup-provider-objects
	mkdir -p ../../../build/bootloader-completion/thread-clock-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../port_timer/port_timer.c -o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../clock_manager/clock_manager.c -o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o
	$(LD) -T startup_clock_integrated.ld -o ../../../build/bootloader-completion/thread-clock-startup-compatible/startup-clock.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o
	$(PYTHON) verify_clock_integrated.py --elf ../../../build/bootloader-completion/thread-clock-startup-compatible/startup-clock.elf --output ../../../build/bootloader-completion/thread-clock-startup-compatible/comparison-first.json

# Build-only prerequisites for the newer integration profiles. These rebuild
# owned source objects rather than depending on objects from earlier tests.
.PHONY: startup-provider-objects timer-integrated-compatible nor-integrated-compatible clock-integrated-compatible svc-compatible
startup-provider-objects:
	$(MAKE) -C ../main_callback startup-integrated-compatible
	$(MAKE) -C ../allocator all CPU=cortex-m4 OUT=../../../build/bootloader-completion/allocator-compatible
	$(MAKE) -C ../nor_init all
	mkdir -p ../../../build/bootloader-completion/thread-runtime-compatible ../../../build/bootloader-completion/thread-port-compatible ../../../build/bootloader-completion/thread-allocator-startup-compatible ../../../build/bootloader-completion/thread-timer-startup-compatible
	for name in thread_creation kernel_static thread_register kernel_runtime; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-runtime-compatible/$$name.o || exit; done
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-runtime-compatible/runtime_mode.o
	for name in scheduler_bootstrap timer_service thread_select port_start; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-port-compatible/$$name.o || exit; done
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c first_task_transfer.S -o ../../../build/bootloader-completion/thread-port-compatible/first_task_transfer.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c lifecycle.c -o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../port_timer/port_timer.c -o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o

svc-compatible: pendsv-compatible
	$(PYTHON) verify_svc.py --elf ../../../build/bootloader-completion/thread-pendsv-compatible/pendsv.elf --output ../../../build/bootloader-completion/thread-pendsv-compatible/svc-comparison.json

priority-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-priority-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c thread_priority.c -o ../../../build/bootloader-completion/thread-priority-compatible/thread_priority.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c kernel_runtime.c -o ../../../build/bootloader-completion/thread-priority-compatible/kernel_runtime.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-priority-compatible/runtime_mode.o
	$(LD) -T priority_module.ld -o ../../../build/bootloader-completion/thread-priority-compatible/priority.elf ../../../build/bootloader-completion/thread-priority-compatible/*.o
	$(PYTHON) verify_priority.py --elf ../../../build/bootloader-completion/thread-priority-compatible/priority.elf --output ../../../build/bootloader-completion/thread-priority-compatible/comparison.json

mspi-integrated-compatible: startup-provider-objects
	$(MAKE) -C ../nor_mspi_init all
	mkdir -p ../../../build/bootloader-completion/thread-mspi-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../clock_manager/clock_manager.c -o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o
	$(LD) -T startup_mspi_integrated.ld -o ../../../build/bootloader-completion/thread-mspi-startup-compatible/startup-mspi.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/nor-mspi-init/*.o
	$(PYTHON) verify_mspi_integrated.py --elf ../../../build/bootloader-completion/thread-mspi-startup-compatible/startup-mspi.elf --output ../../../build/bootloader-completion/thread-mspi-startup-compatible/comparison-first.json
