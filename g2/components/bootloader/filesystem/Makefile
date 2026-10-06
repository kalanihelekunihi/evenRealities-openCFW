# SPDX-License-Identifier: MIT
CC = clang
OUT ?= ../../../build/bootloader-completion/filesystem
HOSTFLAGS = -std=c11 -O2 -Wall -Wextra -Werror -DOPENCFW_BOOT_FS_TEST -DLFS_NO_DEBUG -DLFS_NO_WARN -DLFS_NO_ERROR
.PHONY: host-test
host-test:
	mkdir -p $(OUT)
	$(CC) $(HOSTFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer filesystem.c file_services.c upstream/lfs.c upstream/lfs_util.c host_test.c -o $(OUT)/host-test
	$(OUT)/host-test

# Isolated focused fixture for the exact 0x421210 source provider. Keep its
# output outside the shared ARM integration build directory.
BOOT_MOUNT_TEST_OUT ?= /tmp/opencfw-boot-mount-test
.PHONY: host-boot-mount-test
host-boot-mount-test:
	mkdir -p $(BOOT_MOUNT_TEST_OUT)
	$(CC) $(HOSTFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer filesystem.c boot_mount.c runtime_memory.c upstream/lfs.c upstream/lfs_util.c boot_mount_test.c -o $(BOOT_MOUNT_TEST_OUT)/boot-mount-test
	$(BOOT_MOUNT_TEST_OUT)/boot-mount-test
LD = arm-none-eabi-ld
CPU ?= cortex-m55
ARMFLAGS = --target=arm-none-eabi -mcpu=$(CPU) -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -O2 -fwrapv -Wall -Wextra -Werror -I. -Ifreestanding_include -DLFS_NO_DEBUG -DLFS_NO_WARN -DLFS_NO_ERROR -DLFS_NO_ASSERT -DLFS_NO_INTRINSICS -DLFS_DEFINES=boot_lfs_defines.h
.PHONY: arm-library
arm-library:
	mkdir -p $(OUT)
	$(CC) $(ARMFLAGS) -c filesystem.c -o $(OUT)/filesystem.o
	$(CC) $(ARMFLAGS) -c file_services.c -o $(OUT)/file_services.o
	$(CC) $(ARMFLAGS) -c runtime_memory.c -o $(OUT)/runtime_memory.o
	$(CC) $(ARMFLAGS) -c upstream/lfs.c -o $(OUT)/lfs.o
	$(CC) $(ARMFLAGS) -c upstream/lfs_util.c -o $(OUT)/lfs_util.o
	$(CC) $(ARMFLAGS) -c ../update_core/update_core.c -o $(OUT)/update_core.o
	$(CC) $(ARMFLAGS) -c ../update_core/handoff.S -o $(OUT)/handoff.o
	$(CC) $(ARMFLAGS) -c ../update_core/rom_resources.c -o $(OUT)/rom_resources.o
	$(LD) -T module.ld -o $(OUT)/filesystem-update.elf $(OUT)/filesystem.o $(OUT)/file_services.o $(OUT)/runtime_memory.o $(OUT)/lfs.o $(OUT)/lfs_util.o $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o

# Same real filesystem/update source, now with real pinned TLSF heap ownership.
.PHONY: arm-owned-library
arm-owned-library: arm-library
	$(CC) $(ARMFLAGS) -DNDEBUG -I../allocator/freestanding_include -c ../allocator/allocator.c -o $(OUT)/allocator.o
	$(CC) $(ARMFLAGS) -DNDEBUG -I../allocator/freestanding_include -c ../allocator/upstream/tlsf.c -o $(OUT)/tlsf.o
	$(LD) -T owned_module.ld -o $(OUT)/filesystem-owned-update.elf $(OUT)/filesystem.o $(OUT)/file_services.o $(OUT)/runtime_memory.o $(OUT)/lfs.o $(OUT)/lfs_util.o $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o $(OUT)/allocator.o $(OUT)/tlsf.o

.PHONY: arm-task-library
arm-task-library: arm-owned-library
	$(CC) $(ARMFLAGS) -c ../dfu_task/task.c -o $(OUT)/task.o
	$(LD) -T task_module.ld -o $(OUT)/filesystem-task-update.elf $(OUT)/filesystem.o $(OUT)/file_services.o $(OUT)/runtime_memory.o $(OUT)/lfs.o $(OUT)/lfs_util.o $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o $(OUT)/allocator.o $(OUT)/tlsf.o $(OUT)/task.o

# Replace the queue-wrapper cut with recovered source; kernel remains a boundary.
.PHONY: arm-queue-task-library
arm-queue-task-library: arm-task-library
	$(CC) $(ARMFLAGS) -c ../queue/queue_wrappers.c -o $(OUT)/queue_wrappers.o
	$(LD) -T queue_task_module.ld -o $(OUT)/filesystem-queue-task-update.elf $(OUT)/filesystem.o $(OUT)/file_services.o $(OUT)/runtime_memory.o $(OUT)/lfs.o $(OUT)/lfs_util.o $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o $(OUT)/allocator.o $(OUT)/tlsf.o $(OUT)/task.o $(OUT)/queue_wrappers.o

.PHONY: arm-queue-runtime-task-library
arm-queue-runtime-task-library: arm-queue-task-library
	$(CC) $(ARMFLAGS) -c ../queue/runtime_mode.c -o $(OUT)/queue_runtime.o
	$(LD) -T queue_runtime_task_module.ld -o $(OUT)/filesystem-queue-runtime-task-update.elf $(OUT)/filesystem.o $(OUT)/file_services.o $(OUT)/runtime_memory.o $(OUT)/lfs.o $(OUT)/lfs_util.o $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o $(OUT)/allocator.o $(OUT)/tlsf.o $(OUT)/task.o $(OUT)/queue_wrappers.o $(OUT)/queue_runtime.o

.PHONY: arm-nor-queue-runtime-task-library
arm-nor-queue-runtime-task-library: arm-queue-runtime-task-library
	$(CC) $(ARMFLAGS) -fshort-enums -c ../nor_read/nor_read.c -o $(OUT)/nor_read.o
	$(LD) -T nor_queue_runtime_task_module.ld -o $(OUT)/filesystem-nor-queue-runtime-task-update.elf $(OUT)/filesystem.o $(OUT)/file_services.o $(OUT)/runtime_memory.o $(OUT)/lfs.o $(OUT)/lfs_util.o $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o $(OUT)/allocator.o $(OUT)/tlsf.o $(OUT)/task.o $(OUT)/queue_wrappers.o $(OUT)/queue_runtime.o $(OUT)/nor_read.o

.PHONY: arm-mutex-nor-queue-runtime-task-library
arm-mutex-nor-queue-runtime-task-library: arm-nor-queue-runtime-task-library
	$(CC) $(ARMFLAGS) -c ../queue/mutex.c -o $(OUT)/mutex.o
	$(LD) -T mutex_nor_queue_runtime_task_module.ld -o $(OUT)/filesystem-mutex-nor-queue-runtime-task-update.elf $(OUT)/filesystem.o $(OUT)/file_services.o $(OUT)/runtime_memory.o $(OUT)/lfs.o $(OUT)/lfs_util.o $(OUT)/update_core.o $(OUT)/handoff.o $(OUT)/rom_resources.o $(OUT)/allocator.o $(OUT)/tlsf.o $(OUT)/task.o $(OUT)/queue_wrappers.o $(OUT)/queue_runtime.o $(OUT)/nor_read.o $(OUT)/mutex.o
