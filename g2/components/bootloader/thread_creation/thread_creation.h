/* SPDX-License-Identifier: MIT. ARM32 recovered contracts, not a public SDK. */
#ifndef OPENCFW_BOOT_THREAD_CREATION_H
#define OPENCFW_BOOT_THREAD_CREATION_H
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t name_address, attribute_bits;
    uint32_t control_block_address, control_block_bytes;
    uint32_t stack_address, stack_bytes, raw_priority;
    uint32_t raw_word7, raw_word8;
} opencfw_boot_thread_attributes;
_Static_assert(sizeof(opencfw_boot_thread_attributes)==36,"ARM32 attributes");
_Static_assert(offsetof(opencfw_boot_thread_attributes,raw_priority)==24,"priority offset");
uint32_t opencfw_boot_thread_new(uintptr_t entry,uintptr_t arg,const uint32_t *attr);
int32_t opencfw_boot_kernel_initialize(void);
uint32_t opencfw_boot_kernel_state(void);
int32_t opencfw_boot_kernel_start(void);
void opencfw_boot_thread_select(void);
uintptr_t opencfw_boot_thread_current(void);
int32_t opencfw_boot_thread_priority_set(uintptr_t handle,uint32_t priority);
void opencfw_bl_scheduler_suspend(void);
uint32_t opencfw_bl_scheduler_resume(void);
uintptr_t opencfw_bl_rtos_allocate(uint32_t bytes);
void opencfw_bl_rtos_free(uintptr_t memory);
#endif
