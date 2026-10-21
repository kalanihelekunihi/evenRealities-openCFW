/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_ALLOCATOR_H
#define OPENCFW_BOOT_ALLOCATOR_H
#include <stdint.h>
#include <stddef.h>
#define OPENCFW_BOOT_ARENA_BASE 0x20081000u
#define OPENCFW_BOOT_ARENA_SIZE 0x70800u
uint32_t opencfw_boot_allocator_init(void);
void *opencfw_boot_fs_alloc(uint32_t);
void opencfw_boot_fs_free(void *);
void *opencfw_boot_allocator_core(void);
#endif
