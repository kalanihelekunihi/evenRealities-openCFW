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
	for name in timer_wait queue_receive queue_send event_waiter_wake queue_buffer_release resource_creators timer_commands timer_expiration thread_notifications event_flags_set; do $(CC) $(CFLAGS) -c $$name.c -o ../../../build/bootloader-completion/thread-source-m55/$$name.o
	for name in flags_runtime cmsis_notifications; do $(CC) $(CFLAGS) -c ../flags_runtime/$$name.c -o ../../../build/bootloader-completion/thread-source-m55/$$name.o
	for name in clock_manager clock_class_providers clock_class_provider2 clock_class_provider4 clock_class_provider5 clock_class_provider6; do $(CC) $(CFLAGS) -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c ../clock_manager/$$name.c -o ../../../build/bootloader-completion/thread-source-m55/$$name.o
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
	for path in ../platform_control/runtime.c ../platform_control/runtime_resources.c ../platform_control/runtime_transition.c ../platform_control/runtime_query.c ../platform_control/runtime_wait_adapter.c ../nor_init/nor_runtime.c ../nor_mspi_init/hal_leaves.c ../nor_mspi_init/blocking_transfer.c ../nor_mspi_init/fifo_transfer.c ../nor_mspi_init/status_poll.c; do $(CC) $(CFLAGS) -c $$path -o ../../../build/bootloader-completion/thread-source-m55/$$(basename
	$(CC) --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -c ../nor_mspi_init/irq_guard.S -o ../../../build/bootloader-completion/thread-source-m55/irq_guard.o


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
	for name in thread_creation kernel_static thread_register kernel_runtime; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-runtime-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-runtime-compatible/runtime_mode.o
	for name in scheduler_bootstrap timer_service thread_select port_start; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-port-compatible/$$name.o
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
	mkdir -p ../../../build/bootloader-completion/thread-mspi-startup-compatible ../../../build/bootloader-completion/thread-clock-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../clock_manager/clock_manager.c -o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../clock_manager/clock_class_providers.c -o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c ../clock_manager/clock_class_provider4.c -o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o
	for id in 2 5 6; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c ../clock_manager/clock_class_provider$$id.c -o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider$$id.o
	$(LD) -T startup_mspi_integrated.ld -o ../../../build/bootloader-completion/thread-mspi-startup-compatible/startup-mspi.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o
	$(PYTHON) verify_mspi_integrated.py --elf ../../../build/bootloader-completion/thread-mspi-startup-compatible/startup-mspi.elf --output ../../../build/bootloader-completion/thread-mspi-startup-compatible/comparison-first.json

.PHONY: nor-commands-integrated-compatible
nor-commands-integrated-compatible: mspi-integrated-compatible
	mkdir -p ../../../build/bootloader-completion/thread-nor-commands-startup-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_commands/nor_commands.c -o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o
	$(LD) --gc-sections -T startup_nor_commands_integrated.ld -o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/startup-nor-commands.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o
	$(PYTHON) verify_nor_commands_integrated.py --elf ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/startup-nor-commands.elf --output ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/comparison.json

# Bounded regression profile, NOT a bootable or byte-identical payload target.
.PHONY: completion-regressions
completion-regressions: mspi-fifo-poll-compatible filesystem-update-compatible mspi-blocking-compatible dfu-storage-compatible dfu-runtime-compatible nor-runtime-compatible mspi-leaves-compatible timer-expiration-compatible resource-creators-compatible dfu-dispatch-compatible queue-receive-compatible notifications-compatible event-flags-set-compatible nor-commands-integrated-compatible source-m55-all priority-compatible svc-compatible tick-compatible heap-compatible owned-heap-compatible
	$(MAKE) -C ../../../analysis/bootloader-completion-2026-10-06/upstream-worker/timer-commands test
	$(MAKE) -C ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/queue-buffer-release verify
	$(MAKE) -C ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/queue-send verify
	$(MAKE) -C ../../../analysis/bootloader-completion-2026-10-06/upstream-worker/event-waiter-wake test
	$(MAKE) -C ../../../analysis/bootloader-completion-2026-10-06/upstream-worker/dfu-runtime-context test
	$(MAKE) -C ../flags_runtime verify
	$(MAKE) -C ../manager_task handshake-compatible
	$(MAKE) -C ../../../analysis/bootloader-completion-2026-10-06/upstream-worker/clock-manager OUT=out/repro test
	$(MAKE) -C ../manager_task verify sender-integrated setup-compatible event-compatible dispatch-compatible
	$(MAKE) -C ../nor_commands verify

.PHONY: timer-wait-compatible
timer-wait-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-timer-wait-compatible
	for name in timer_wait kernel_runtime scheduler_resume; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-timer-wait-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-timer-wait-compatible/runtime_mode.o
	$(LD) -T timer_wait_module.ld -o ../../../build/bootloader-completion/thread-timer-wait-compatible/timer-wait.elf ../../../build/bootloader-completion/thread-timer-wait-compatible/*.o
	$(PYTHON) verify_timer_wait.py --elf ../../../build/bootloader-completion/thread-timer-wait-compatible/timer-wait.elf --output ../../../build/bootloader-completion/thread-timer-wait-compatible/comparison.json

.PHONY: manager-bridge-compatible
manager-bridge-compatible: nor-commands-integrated-compatible timer-wait-compatible
	mkdir -p ../../../build/bootloader-completion/thread-manager-bridge-compatible
	for name in timer_wait queue_receive queue_send event_waiter_wake queue_buffer_release resource_creators timer_commands timer_expiration kernel_dynamic rtos_heap scheduler_resume scheduler_tick thread_priority thread_notifications event_flags_set; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c $$name.c -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/$$name.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c exception_entry.S -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/exception_entry.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -c task_entry_adapters.S -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/task_entry_adapters.o
	for name in manager_task manager_setup event_runtime event_dispatch manager_handshake; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../manager_task/$$name.c -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/$$name.o
	for name in flags_runtime cmsis_notifications; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../flags_runtime/$$name.c -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../dfu_task/runtime_context.c -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/runtime_context.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -DOPENCFW_DFU_TASK_AT_STOCK_ADDRESS -c ../dfu_task/context.c -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/context.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../queue/queue_wrappers.c -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/queue_wrappers.o
	$(LD) --gc-sections -T startup_manager_bridge.ld -o ../../../build/bootloader-completion/thread-manager-bridge-compatible/manager-bridge.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o
	$(PYTHON) verify_manager_bridge.py --elf ../../../build/bootloader-completion/thread-manager-bridge-compatible/manager-bridge.elf --output ../../../build/bootloader-completion/thread-manager-bridge-compatible/comparison.json

.PHONY: queue-receive-compatible
queue-receive-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-queue-receive-compatible
	for name in queue_receive timer_wait kernel_runtime scheduler_resume; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-queue-receive-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-queue-receive-compatible/runtime_mode.o
	$(LD) -T queue_receive_module.ld -o ../../../build/bootloader-completion/thread-queue-receive-compatible/queue-receive.elf ../../../build/bootloader-completion/thread-queue-receive-compatible/*.o
	$(PYTHON) verify_queue_receive.py --elf ../../../build/bootloader-completion/thread-queue-receive-compatible/queue-receive.elf --output ../../../build/bootloader-completion/thread-queue-receive-compatible/comparison.json

.PHONY: notifications-compatible
notifications-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-notifications-compatible
	for name in thread_notifications timer_wait kernel_runtime scheduler_resume; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-notifications-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-notifications-compatible/runtime_mode.o
	$(LD) -T notifications_module.ld -o ../../../build/bootloader-completion/thread-notifications-compatible/notifications.elf ../../../build/bootloader-completion/thread-notifications-compatible/*.o
	$(PYTHON) verify_notifications.py --elf ../../../build/bootloader-completion/thread-notifications-compatible/notifications.elf --output ../../../build/bootloader-completion/thread-notifications-compatible/comparison.json

.PHONY: event-flags-set-compatible
event-flags-set-compatible:
	mkdir -p ../../../build/bootloader-completion/thread-event-flags-set-compatible
	for name in event_flags_set timer_wait kernel_runtime scheduler_resume; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -c $$name.c -o ../../../build/bootloader-completion/thread-event-flags-set-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c ../queue/runtime_mode.c -o ../../../build/bootloader-completion/thread-event-flags-set-compatible/runtime_mode.o
	$(LD) -T event_flags_set_module.ld -o ../../../build/bootloader-completion/thread-event-flags-set-compatible/event-flags-set.elf ../../../build/bootloader-completion/thread-event-flags-set-compatible/*.o
	$(PYTHON) verify_event_flags_set.py --elf ../../../build/bootloader-completion/thread-event-flags-set-compatible/event-flags-set.elf --output ../../../build/bootloader-completion/thread-event-flags-set-compatible/comparison.json

.PHONY: reset-manager-compatible
reset-manager-compatible: manager-bridge-compatible
	mkdir -p ../../../build/bootloader-completion/reset-manager-compatible
	for name in reset fpu; do $(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c ../startup/$$name.S -o ../../../build/bootloader-completion/reset-manager-compatible/$$name.o
	$(LD) --gc-sections -T startup_reset_manager.ld -o ../../../build/bootloader-completion/reset-manager-compatible/reset-manager.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o
	$(PYTHON) verify_reset_manager.py --elf ../../../build/bootloader-completion/reset-manager-compatible/reset-manager.elf --output ../../../build/bootloader-completion/reset-manager-compatible/comparison.json

.PHONY: resource-creators-compatible
resource-creators-compatible:
	mkdir -p ../../../build/bootloader-completion/resource-creators-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m4 -c resource_creators.c -o ../../../build/bootloader-completion/resource-creators-compatible/resource_creators.o
	$(LD) -T resource_creators_module.ld -o ../../../build/bootloader-completion/resource-creators-compatible/resource-creators.elf ../../../build/bootloader-completion/resource-creators-compatible/resource_creators.o
	$(PYTHON) verify_resource_creators.py --elf ../../../build/bootloader-completion/resource-creators-compatible/resource-creators.elf --output ../../../build/bootloader-completion/resource-creators-compatible/comparison.json

.PHONY: dfu-dispatch-compatible
dfu-dispatch-compatible: reset-manager-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-dispatch-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -I../filesystem/freestanding_include -c ../dfu_task/task.c -o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o
	for name in update_core rom_resources; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../update_core/$$name.c -o ../../../build/bootloader-completion/dfu-dispatch-compatible/$$name.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -c ../update_core/handoff.S -o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o
	$(LD) --gc-sections -T startup_dfu_dispatch.ld -o ../../../build/bootloader-completion/dfu-dispatch-compatible/dfu-dispatch.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o
	$(PYTHON) verify_manager_bridge.py --reset --dispatch --elf ../../../build/bootloader-completion/dfu-dispatch-compatible/dfu-dispatch.elf --output ../../../build/bootloader-completion/dfu-dispatch-compatible/comparison.json

.PHONY: timer-expiration-compatible
timer-expiration-compatible:
	mkdir -p ../../../build/bootloader-completion/timer-expiration-compatible
	for name in timer_expiration timer_commands timer_wait; do $(CC) $(CFLAGS) -mcpu=cortex-m4 -ffunction-sections -c $$name.c -o ../../../build/bootloader-completion/timer-expiration-compatible/$$name.o
	$(LD) --gc-sections --undefined=opencfw_bl_timer_rollover -T ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/timer-expiration/timer_expiration_test.ld -o ../../../build/bootloader-completion/timer-expiration-compatible/timer-expiration.elf ../../../build/bootloader-completion/timer-expiration-compatible/*.o
	$(PYTHON) ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/timer-expiration/verify_timer_expiration.py --elf ../../../build/bootloader-completion/timer-expiration-compatible/timer-expiration.elf --output ../../../build/bootloader-completion/timer-expiration-compatible/comparison.json

.PHONY: dfu-runtime-compatible nor-runtime-compatible mspi-leaves-compatible
dfu-runtime-compatible: dfu-dispatch-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-runtime-compatible
	for name in control runtime runtime_resources runtime_transition runtime_query runtime_wait_adapter; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../platform_control/$$name.c -o ../../../build/bootloader-completion/dfu-runtime-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_init/nor_runtime.c -o ../../../build/bootloader-completion/dfu-runtime-compatible/nor_runtime.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_mspi_init/hal_leaves.c -o ../../../build/bootloader-completion/dfu-runtime-compatible/hal_leaves.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_mspi_init/blocking_transfer.c -o ../../../build/bootloader-completion/dfu-runtime-compatible/blocking_transfer.o
	for name in fifo_transfer status_poll; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_mspi_init/$$name.c -o ../../../build/bootloader-completion/dfu-runtime-compatible/$$name.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -c ../platform_control/critical_save.S -o ../../../build/bootloader-completion/dfu-runtime-compatible/critical_save.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -c ../nor_mspi_init/irq_guard.S -o ../../../build/bootloader-completion/dfu-runtime-compatible/irq_guard.o
	$(LD) --gc-sections -T startup_dfu_runtime.ld -o ../../../build/bootloader-completion/dfu-runtime-compatible/dfu-runtime.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o
	$(PYTHON) verify_dfu_runtime.py --elf ../../../build/bootloader-completion/dfu-runtime-compatible/dfu-runtime.elf --output ../../../build/bootloader-completion/dfu-runtime-compatible/comparison.json
nor-runtime-compatible:
	mkdir -p ../../../build/bootloader-completion/nor-runtime-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../nor_init/nor_runtime.c -o ../../../build/bootloader-completion/nor-runtime-compatible/nor_runtime.o
	$(LD) -T ../nor_init/runtime_module.ld -o ../../../build/bootloader-completion/nor-runtime-compatible/nor-runtime.elf ../../../build/bootloader-completion/nor-runtime-compatible/nor_runtime.o
	$(PYTHON) ../nor_init/verify_runtime.py --elf ../../../build/bootloader-completion/nor-runtime-compatible/nor-runtime.elf --output ../../../build/bootloader-completion/nor-runtime-compatible/comparison.json
mspi-leaves-compatible:
	mkdir -p ../../../build/bootloader-completion/mspi-leaves-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../nor_mspi_init/hal_leaves.c -o ../../../build/bootloader-completion/mspi-leaves-compatible/hal_leaves.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -c ../nor_mspi_init/irq_guard.S -o ../../../build/bootloader-completion/mspi-leaves-compatible/irq_guard.o
	$(LD) -T ../nor_mspi_init/leaves_module.ld -o ../../../build/bootloader-completion/mspi-leaves-compatible/mspi-leaves.elf ../../../build/bootloader-completion/mspi-leaves-compatible/*.o
	$(PYTHON) ../nor_mspi_init/verify_leaves.py --elf ../../../build/bootloader-completion/mspi-leaves-compatible/mspi-leaves.elf --output ../../../build/bootloader-completion/mspi-leaves-compatible/comparison.json

.PHONY: mspi-blocking-compatible
mspi-blocking-compatible:
	mkdir -p ../../../build/bootloader-completion/mspi-blocking-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../nor_mspi_init/blocking_transfer.c -o ../../../build/bootloader-completion/mspi-blocking-compatible/blocking_transfer.o
	$(LD) -T ../nor_mspi_init/blocking_module.ld -o ../../../build/bootloader-completion/mspi-blocking-compatible/mspi-blocking.elf ../../../build/bootloader-completion/mspi-blocking-compatible/blocking_transfer.o
	$(PYTHON) ../nor_mspi_init/verify_blocking.py --elf ../../../build/bootloader-completion/mspi-blocking-compatible/mspi-blocking.elf --output ../../../build/bootloader-completion/mspi-blocking-compatible/comparison.json

.PHONY: filesystem-update-compatible
filesystem-update-compatible:
	$(MAKE) -C ../filesystem arm-nor-queue-runtime-task-library CPU=cortex-m4
	$(PYTHON) ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/filesystem-update/verify_file_services_differential.py --elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/filesystem-update/file-services-comparison.json
	$(PYTHON) ../filesystem/verify_arm.py --elf ../../../build/bootloader-completion/filesystem/filesystem-nor-queue-runtime-task-update.elf --output ../../../analysis/bootloader-completion-2026-10-06/inventory-worker/filesystem-update/source-task-update-real-read.json --real-allocator --real-task --real-queue --real-queue-runtime --real-nor-read

.PHONY: mspi-fifo-poll-compatible
mspi-fifo-poll-compatible:
	mkdir -p ../../../build/bootloader-completion/mspi-fifo-poll-compatible
	for name in fifo_transfer status_poll; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../nor_mspi_init/$$name.c -o ../../../build/bootloader-completion/mspi-fifo-poll-compatible/$$name.o
	$(LD) -T ../nor_mspi_init/fifo_module.ld -o ../../../build/bootloader-completion/mspi-fifo-poll-compatible/fifo.elf ../../../build/bootloader-completion/mspi-fifo-poll-compatible/fifo_transfer.o
	$(LD) -T ../nor_mspi_init/poll_module.ld -o ../../../build/bootloader-completion/mspi-fifo-poll-compatible/poll.elf ../../../build/bootloader-completion/mspi-fifo-poll-compatible/status_poll.o
	$(PYTHON) ../nor_mspi_init/verify_fifo_poll.py --fifo-elf ../../../build/bootloader-completion/mspi-fifo-poll-compatible/fifo.elf --poll-elf ../../../build/bootloader-completion/mspi-fifo-poll-compatible/poll.elf --output ../../../build/bootloader-completion/mspi-fifo-poll-compatible/comparison.json

.PHONY: dfu-storage-compatible
dfu-storage-compatible: dfu-runtime-compatible filesystem-update-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-storage-compatible
	for path in ../filesystem/filesystem.c ../filesystem/file_services.c ../filesystem/boot_mount.c ../filesystem/upstream/lfs.c ../filesystem/upstream/lfs_util.c; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -I../filesystem/freestanding_include -I../filesystem -DLFS_NO_DEBUG -DLFS_NO_WARN -DLFS_NO_ERROR -DLFS_NO_ASSERT -DLFS_NO_INTRINSICS -DLFS_DEFINES=boot_lfs_defines.h -c $$path -o ../../../build/bootloader-completion/dfu-storage-compatible/$$(basename
	$(LD) --gc-sections -T startup_dfu_storage.ld -o ../../../build/bootloader-completion/dfu-storage-compatible/dfu-storage.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o
	$(PYTHON) verify_dfu_storage.py --elf ../../../build/bootloader-completion/dfu-storage-compatible/dfu-storage.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/dfu-storage-compatible/comparison.json

.PHONY: dfu-storage-read-compatible
dfu-storage-read-compatible: dfu-storage-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-storage-read-compatible
	for name in nor_read runtime_helpers; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -fshort-enums -ffunction-sections -c ../nor_read/$$name.c -o ../../../build/bootloader-completion/dfu-storage-read-compatible/$$name.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_mspi_init/control_read.c -o ../../../build/bootloader-completion/dfu-storage-read-compatible/control_read.o
	$(LD) --gc-sections -T startup_dfu_storage_read.ld -o ../../../build/bootloader-completion/dfu-storage-read-compatible/dfu-storage-read.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o ../../../build/bootloader-completion/dfu-storage-read-compatible/*.o
	$(PYTHON) verify_dfu_storage_read.py --elf ../../../build/bootloader-completion/dfu-storage-read-compatible/dfu-storage-read.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/dfu-storage-read-compatible/comparison.json

.PHONY: dfu-storage-nor-compatible
dfu-storage-nor-compatible: dfu-storage-read-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-storage-nor-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_write/nor_write.c -o ../../../build/bootloader-completion/dfu-storage-nor-compatible/nor_write.o
	$(LD) --gc-sections -T startup_dfu_storage_nor.ld -o ../../../build/bootloader-completion/dfu-storage-nor-compatible/dfu-storage-nor.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o ../../../build/bootloader-completion/dfu-storage-read-compatible/*.o ../../../build/bootloader-completion/dfu-storage-nor-compatible/*.o
	$(PYTHON) verify_dfu_storage_nor.py --elf ../../../build/bootloader-completion/dfu-storage-nor-compatible/dfu-storage-nor.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/dfu-storage-nor-compatible/comparison.json

.PHONY: dfu-storage-power-compatible
dfu-storage-power-compatible: dfu-storage-nor-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-storage-power-compatible
	for path in ../nor_mspi_power/power_control.c ../nor_mspi_power/power_control_adapter.c ../nor_mspi_power/device_configure.c ../nor_mspi_power/mspi_clockgen_control.c ../platform_control/power_domains.c ../clock_manager/clock_release_all.c; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c $$path -o ../../../build/bootloader-completion/dfu-storage-power-compatible/$$(basename
	$(LD) --gc-sections -T startup_dfu_storage_power.ld -o ../../../build/bootloader-completion/dfu-storage-power-compatible/dfu-storage-power.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o ../../../build/bootloader-completion/dfu-storage-read-compatible/*.o ../../../build/bootloader-completion/dfu-storage-nor-compatible/*.o ../../../build/bootloader-completion/dfu-storage-power-compatible/*.o
	$(PYTHON) verify_dfu_storage_power.py --elf ../../../build/bootloader-completion/dfu-storage-power-compatible/dfu-storage-power.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/dfu-storage-power-compatible/comparison.json

.PHONY: dfu-storage-queue-compatible
dfu-storage-queue-compatible: dfu-storage-power-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-storage-queue-compatible
	for path in ../nor_mspi_queue/nor_mspi_queue.c ../nor_mspi_queue/resources.c; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -DOPENCFW_USE_EXTERNAL_MSPI_CLOCKGEN -c $$path -o ../../../build/bootloader-completion/dfu-storage-queue-compatible/$$(basename
	$(LD) --gc-sections -T startup_dfu_storage_queue.ld -o ../../../build/bootloader-completion/dfu-storage-queue-compatible/dfu-storage-queue.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o ../../../build/bootloader-completion/dfu-storage-read-compatible/*.o ../../../build/bootloader-completion/dfu-storage-nor-compatible/*.o ../../../build/bootloader-completion/dfu-storage-power-compatible/*.o ../../../build/bootloader-completion/dfu-storage-queue-compatible/*.o
	$(PYTHON) verify_dfu_storage_queue.py --elf ../../../build/bootloader-completion/dfu-storage-queue-compatible/dfu-storage-queue.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/dfu-storage-queue-compatible/comparison.json

.PHONY: dfu-storage-cache-compatible
dfu-storage-cache-compatible: dfu-storage-queue-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-storage-cache-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../platform_control/cache_runtime.c -o ../../../build/bootloader-completion/dfu-storage-cache-compatible/cache_runtime.o
	$(LD) --gc-sections -T startup_dfu_storage_cache.ld -o ../../../build/bootloader-completion/dfu-storage-cache-compatible/dfu-storage-cache.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o ../../../build/bootloader-completion/dfu-storage-read-compatible/*.o ../../../build/bootloader-completion/dfu-storage-nor-compatible/*.o ../../../build/bootloader-completion/dfu-storage-power-compatible/*.o ../../../build/bootloader-completion/dfu-storage-queue-compatible/*.o ../../../build/bootloader-completion/dfu-storage-cache-compatible/*.o
	$(PYTHON) verify_dfu_storage_cache.py --elf ../../../build/bootloader-completion/dfu-storage-cache-compatible/dfu-storage-cache.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/dfu-storage-cache-compatible/comparison.json

.PHONY: dfu-storage-platform-compatible
dfu-storage-platform-compatible: dfu-storage-cache-compatible
	mkdir -p ../../../build/bootloader-completion/dfu-storage-platform-compatible
	for path in ../nor_mspi_init/control_remaining.c ../nor_mspi_init/control_request_extension.c ../nor_mspi_init/control_request_state.c ../nor_mspi_init/control_request_clock.c ../nor_mspi_init/control_request_transactions.c ../nor_mspi_init/control_request34.c ../nor_mspi_init/control_request_helpers.c ../nor_mspi_queue/queue_descriptors.c ../nor_mspi_queue/mspi_pause_dma.c ../platform_startup/platform_startup.c ../application_storage/storage_callbacks.c ../application_storage/device_info.c ../application_storage/device_info_dispatch.c ../application_storage/device_info_mode0.c ../application_storage/device_mode_wait.c ../application_storage/device_wait_service.c ../application_storage/info_read_rom_thunk.S ../application_storage/storage_callback_veneers.S ../platform_control/power_guards.c ../platform_control/mram_rom_bridge.c; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c $$path -o ../../../build/bootloader-completion/dfu-storage-platform-compatible/$$(basename
	$(LD) --gc-sections -T startup_dfu_storage_platform.ld -o ../../../build/bootloader-completion/dfu-storage-platform-compatible/dfu-storage-platform.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o ../../../build/bootloader-completion/dfu-storage-read-compatible/*.o ../../../build/bootloader-completion/dfu-storage-nor-compatible/*.o ../../../build/bootloader-completion/dfu-storage-power-compatible/*.o ../../../build/bootloader-completion/dfu-storage-queue-compatible/*.o ../../../build/bootloader-completion/dfu-storage-cache-compatible/*.o ../../../build/bootloader-completion/dfu-storage-platform-compatible/*.o
	$(PYTHON) verify_dfu_storage_platform.py --elf ../../../build/bootloader-completion/dfu-storage-platform-compatible/dfu-storage-platform.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/dfu-storage-platform-compatible/comparison.json

.PHONY: source-image-compatible
source-image-compatible: dfu-storage-platform-compatible
	mkdir -p ../../../build/bootloader-completion/source-image-compatible
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../platform_startup/local_providers.S -o ../../../build/bootloader-completion/source-image-compatible/local_providers.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../platform_startup/delay_math.S -o ../../../build/bootloader-completion/source-image-compatible/delay_math.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../platform_control/cache_enable.c -o ../../../build/bootloader-completion/source-image-compatible/cache_enable.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../nor_mspi_init/register_id.c -o ../../../build/bootloader-completion/source-image-compatible/register_id.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../clock_manager/mode_publisher.c -o ../../../build/bootloader-completion/source-image-compatible/mode_publisher.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -ffunction-sections -c ../clock_manager/mode_publisher_abi.S -o ../../../build/bootloader-completion/source-image-compatible/mode_publisher_abi.o
	for path in ../nor_mspi_power/serial_mode_switch.c ../nor_mspi_power/xip_address_mode.c ../nor_mspi_power/timing_scan.c ../nor_commands/nor_timing_wrapper.S ../initializer_callbacks/callback_table.S ../init_table/init_table.c ../init_table/qsort.c ../initializer_callbacks/initializer_callbacks.c ../initializer_callbacks/mode_register.c ../initializer_callbacks/platform_finish.c ../initializer_callbacks/context_interrupt.c ../initializer_callbacks/context_claim.c ../initializer_callbacks/context_transaction.c ../initializer_callbacks/context_instance.c ../initializer_callbacks/context_clock.c ../initializer_callbacks/context_queue.c ../initializer_callbacks/context_retry.c ../initializer_callbacks/context_nvic.c ../initializer_callbacks/semaphore_create.c ../initializer_callbacks/context_events.c ../initializer_callbacks/context_irq.c ../initializer_callbacks/gpio_descriptors.c ../initializer_callbacks/service_records.c ../initializer_callbacks/elog_setters.c mutex_kernel.c isr_delivery.c ../queue/mutex.c ../initializer_callbacks/uart_context.c ../initializer_callbacks/adc_context.c ../initializer_callbacks/adc_configuration.c ../initializer_callbacks/adc_profile.c ../initializer_callbacks/gpio_descriptor_data.c ../initializer_callbacks/post_bringup.c; do $(CC) $(CFLAGS) -mcpu=cortex-m33 -fwrapv -ffunction-sections -fdata-sections -c $$path -o ../../../build/bootloader-completion/source-image-compatible/$$(basename
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -fwrapv -ffunction-sections -fdata-sections -c ../initializer_callbacks/platform_bringup.c -o ../../../build/bootloader-completion/source-image-compatible/platform_bringup.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=softfp -mfpu=fpv5-sp-d16 -ffreestanding -fno-builtin -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -ffunction-sections -fdata-sections -c ../initializer_callbacks/adc_control.c -o ../../../build/bootloader-completion/source-image-compatible/adc_control.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=softfp -mfpu=fpv5-sp-d16 -ffreestanding -fno-builtin -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -ffunction-sections -fdata-sections -c ../initializer_callbacks/adc_samples.c -o ../../../build/bootloader-completion/source-image-compatible/adc_samples.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -fno-inline-functions -ffunction-sections -fdata-sections -c ../initializer_callbacks/elog_output.c -o ../../../build/bootloader-completion/source-image-compatible/elog_output.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -ffunction-sections -fdata-sections -c ../initializer_callbacks/elog_uart_tx.c -o ../../../build/bootloader-completion/source-image-compatible/elog_uart_tx.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -O0 -ffunction-sections -fdata-sections -c ../initializer_callbacks/startup_alternatives.c -o ../../../build/bootloader-completion/source-image-compatible/startup_alternatives.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -ffunction-sections -fdata-sections -c ../initializer_callbacks/startup_config_leaves.c -o ../../../build/bootloader-completion/source-image-compatible/startup_config_leaves.o
	$(CC) --target=arm-none-eabi -mcpu=cortex-m7 -mthumb -mfpu=fpv5-d16 -mfloat-abi=softfp -ffreestanding -fno-builtin -fwrapv -O0 -ffunction-sections -fdata-sections -Wall -Wextra -Werror -c ../initializer_callbacks/plain_printf.c -o ../../../build/bootloader-completion/source-image-compatible/plain_printf.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -ffunction-sections -fdata-sections -c ../initializer_callbacks/startup_clock_config.c -o ../../../build/bootloader-completion/source-image-compatible/startup_clock_config.o
	$(CC) $(CFLAGS) -mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -c ../initializer_callbacks/clock_generators.c -o ../../../build/bootloader-completion/source-image-compatible/clock_generators.o
	$(CC) $(CFLAGS) -mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -c ../initializer_callbacks/clock_pll_math.c -o ../../../build/bootloader-completion/source-image-compatible/clock_pll_math.o
	$(CC) $(CFLAGS) -mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -c ../initializer_callbacks/clock_pll_rounding.c -o ../../../build/bootloader-completion/source-image-compatible/clock_pll_rounding.o
	$(CC) $(CFLAGS) -mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -c ../initializer_callbacks/clock_pll_mod.c -o ../../../build/bootloader-completion/source-image-compatible/clock_pll_mod.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -c ../initializer_callbacks/uart_rx.c -o ../../../build/bootloader-completion/source-image-compatible/uart_rx.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -c ../platform_control/power_special_mode.c -o ../../../build/bootloader-completion/source-image-compatible/power_special_mode.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -c ../initializer_callbacks/startup_shutdown.c -o ../../../build/bootloader-completion/source-image-compatible/startup_shutdown.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -c ../initializer_callbacks/startup_power_config.c -o ../../../build/bootloader-completion/source-image-compatible/startup_power_config.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -c ../initializer_callbacks/startup_initialize_leaves.c -o ../../../build/bootloader-completion/source-image-compatible/startup_initialize_leaves.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1 -c ../initializer_callbacks/startup_spot_handlers.c -o ../../../build/bootloader-completion/source-image-compatible/startup_spot_handlers.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1 -c ../initializer_callbacks/startup_spot_timer.c -o ../../../build/bootloader-completion/source-image-compatible/startup_spot_timer.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1 -c ../initializer_callbacks/startup_ton_hooks.c -o ../../../build/bootloader-completion/source-image-compatible/startup_ton_hooks.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1 -c ../initializer_callbacks/startup_ton_gate.c -o ../../../build/bootloader-completion/source-image-compatible/startup_ton_gate.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1 -mfloat-abi=softfp -mfpu=fpv5-sp-d16 -c ../initializer_callbacks/startup_spot_events.c -o ../../../build/bootloader-completion/source-image-compatible/startup_spot_events.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1 -I ../../../analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/ambiqhal/CMSIS/AmbiqMicro/Include -I ../../../analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/cmsis-5-590/CMSIS/Core/Include -c ../initializer_callbacks/startup_clockmux.c -o ../../../build/bootloader-completion/source-image-compatible/startup_clockmux.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1  -c ../initializer_callbacks/startup_clockmux_dependencies.c -o ../../../build/bootloader-completion/source-image-compatible/startup_clockmux_dependencies.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O1  -c ../initializer_callbacks/startup_power_register_read.c -o ../../../build/bootloader-completion/source-image-compatible/startup_power_register_read.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../initializer_callbacks/startup_clockmux_entry.S -o ../../../build/bootloader-completion/source-image-compatible/startup_clockmux_entry.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -c ../../foundation/cache_maintenance/cache_maintenance.c -o ../../../build/bootloader-completion/source-image-compatible/startup_cache_maintenance.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -c ../initializer_callbacks/startup_runtime.c -o ../../../build/bootloader-completion/source-image-compatible/startup_runtime.o
	$(CC) $(CFLAGS) -mcpu=cortex-m33 -O0 -c ../initializer_callbacks/startup_memory_config.c -o ../../../build/bootloader-completion/source-image-compatible/startup_memory_config.o
	$(LD) --gc-sections -T startup_source_image.ld -o ../../../build/bootloader-completion/source-image-compatible/bootloader-source-test.elf ../../../build/bootloader-completion/main-callback-startup-integrated-compatible/*.o ../../../build/bootloader-completion/thread-runtime-compatible/*.o ../../../build/bootloader-completion/thread-port-compatible/*.o ../../../build/bootloader-completion/allocator-compatible/*.o ../../../build/bootloader-completion/thread-allocator-startup-compatible/lifecycle.o ../../../build/bootloader-completion/thread-timer-startup-compatible/port_timer.o ../../../build/bootloader-completion/nor-init/*.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_manager.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_providers.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider4.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider2.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider5.o ../../../build/bootloader-completion/thread-clock-startup-compatible/clock_class_provider6.o ../../../build/bootloader-completion/nor-mspi-init/*.o ../../../build/bootloader-completion/thread-nor-commands-startup-compatible/nor_commands.o ../../../build/bootloader-completion/thread-manager-bridge-compatible/*.o ../../../build/bootloader-completion/reset-manager-compatible/reset.o ../../../build/bootloader-completion/reset-manager-compatible/fpu.o ../../../build/bootloader-completion/dfu-dispatch-compatible/task.o ../../../build/bootloader-completion/dfu-dispatch-compatible/update_core.o ../../../build/bootloader-completion/dfu-dispatch-compatible/rom_resources.o ../../../build/bootloader-completion/dfu-dispatch-compatible/handoff.o ../../../build/bootloader-completion/dfu-runtime-compatible/*.o ../../../build/bootloader-completion/dfu-storage-compatible/*.o ../../../build/bootloader-completion/dfu-storage-read-compatible/*.o ../../../build/bootloader-completion/dfu-storage-nor-compatible/*.o ../../../build/bootloader-completion/dfu-storage-power-compatible/*.o ../../../build/bootloader-completion/dfu-storage-queue-compatible/*.o ../../../build/bootloader-completion/dfu-storage-cache-compatible/*.o ../../../build/bootloader-completion/dfu-storage-platform-compatible/*.o ../../../build/bootloader-completion/source-image-compatible/local_providers.o ../../../build/bootloader-completion/source-image-compatible/delay_math.o ../../../build/bootloader-completion/source-image-compatible/cache_enable.o ../../../build/bootloader-completion/source-image-compatible/register_id.o ../../../build/bootloader-completion/source-image-compatible/mode_publisher.o ../../../build/bootloader-completion/source-image-compatible/mode_publisher_abi.o ../../../build/bootloader-completion/source-image-compatible/serial_mode_switch.o ../../../build/bootloader-completion/source-image-compatible/xip_address_mode.o ../../../build/bootloader-completion/source-image-compatible/timing_scan.o ../../../build/bootloader-completion/source-image-compatible/nor_timing_wrapper.o ../../../build/bootloader-completion/source-image-compatible/init_table.o ../../../build/bootloader-completion/source-image-compatible/qsort.o ../../../build/bootloader-completion/source-image-compatible/initializer_callbacks.o ../../../build/bootloader-completion/source-image-compatible/mode_register.o ../../../build/bootloader-completion/source-image-compatible/platform_finish.o ../../../build/bootloader-completion/source-image-compatible/context_interrupt.o ../../../build/bootloader-completion/source-image-compatible/context_claim.o ../../../build/bootloader-completion/source-image-compatible/context_transaction.o ../../../build/bootloader-completion/source-image-compatible/context_instance.o ../../../build/bootloader-completion/source-image-compatible/context_clock.o ../../../build/bootloader-completion/source-image-compatible/context_queue.o ../../../build/bootloader-completion/source-image-compatible/context_retry.o ../../../build/bootloader-completion/source-image-compatible/context_nvic.o ../../../build/bootloader-completion/source-image-compatible/semaphore_create.o ../../../build/bootloader-completion/source-image-compatible/context_events.o ../../../build/bootloader-completion/source-image-compatible/context_irq.o ../../../build/bootloader-completion/source-image-compatible/gpio_descriptors.o ../../../build/bootloader-completion/source-image-compatible/service_records.o ../../../build/bootloader-completion/source-image-compatible/elog_setters.o ../../../build/bootloader-completion/source-image-compatible/elog_output.o ../../../build/bootloader-completion/source-image-compatible/elog_uart_tx.o ../../../build/bootloader-completion/source-image-compatible/startup_alternatives.o ../../../build/bootloader-completion/source-image-compatible/startup_config_leaves.o ../../../build/bootloader-completion/source-image-compatible/plain_printf.o ../../../build/bootloader-completion/source-image-compatible/startup_clock_config.o ../../../build/bootloader-completion/source-image-compatible/clock_generators.o ../../../build/bootloader-completion/source-image-compatible/clock_pll_math.o ../../../build/bootloader-completion/source-image-compatible/clock_pll_rounding.o ../../../build/bootloader-completion/source-image-compatible/clock_pll_mod.o ../../../build/bootloader-completion/source-image-compatible/uart_rx.o ../../../build/bootloader-completion/source-image-compatible/power_special_mode.o ../../../build/bootloader-completion/source-image-compatible/startup_shutdown.o ../../../build/bootloader-completion/source-image-compatible/startup_power_config.o ../../../build/bootloader-completion/source-image-compatible/mutex_kernel.o ../../../build/bootloader-completion/source-image-compatible/isr_delivery.o ../../../build/bootloader-completion/source-image-compatible/mutex.o ../../../build/bootloader-completion/source-image-compatible/uart_context.o ../../../build/bootloader-completion/source-image-compatible/adc_context.o ../../../build/bootloader-completion/source-image-compatible/adc_control.o ../../../build/bootloader-completion/source-image-compatible/adc_configuration.o ../../../build/bootloader-completion/source-image-compatible/adc_samples.o ../../../build/bootloader-completion/source-image-compatible/adc_profile.o ../../../build/bootloader-completion/source-image-compatible/gpio_descriptor_data.o ../../../build/bootloader-completion/source-image-compatible/post_bringup.o ../../../build/bootloader-completion/source-image-compatible/platform_bringup.o ../../../build/bootloader-completion/source-image-compatible/callback_table.o ../../../build/bootloader-completion/source-image-compatible/startup_initialize_leaves.o ../../../build/bootloader-completion/source-image-compatible/startup_runtime.o ../../../build/bootloader-completion/source-image-compatible/startup_memory_config.o ../../../build/bootloader-completion/source-image-compatible/startup_spot_handlers.o ../../../build/bootloader-completion/source-image-compatible/startup_spot_timer.o ../../../build/bootloader-completion/source-image-compatible/startup_spot_events.o ../../../build/bootloader-completion/source-image-compatible/startup_clockmux.o ../../../build/bootloader-completion/source-image-compatible/startup_clockmux_entry.o ../../../build/bootloader-completion/source-image-compatible/startup_clockmux_dependencies.o ../../../build/bootloader-completion/source-image-compatible/startup_power_register_read.o ../../../build/bootloader-completion/source-image-compatible/startup_cache_maintenance.o ../../../build/bootloader-completion/source-image-compatible/startup_ton_hooks.o ../../../build/bootloader-completion/source-image-compatible/startup_ton_gate.o
	$(PYTHON) verify_code_alignment.py --elf ../../../build/bootloader-completion/source-image-compatible/bootloader-source-test.elf
	$(PYTHON) verify_source_image.py --elf ../../../build/bootloader-completion/source-image-compatible/bootloader-source-test.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/source-image-compatible/comparison.json
	$(PYTHON) verify_source_image_failures.py --elf ../../../build/bootloader-completion/source-image-compatible/bootloader-source-test.elf --seed-elf ../../../build/bootloader-completion/filesystem/filesystem-update.elf --output ../../../build/bootloader-completion/source-image-compatible/failures.json
