/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2025, Ambiq Micro, Inc.
 *
 * Bounded Apollo510 am_hal_cmdq update_indices adaptation for the G2 ABI.
 * The complete BSD-3-Clause terms are retained in this component's NOTICE.
 */

typedef __UINT32_TYPE__ open_cfw_cmdq_u32;
typedef __INT32_TYPE__ open_cfw_cmdq_s32;

typedef struct open_cfw_cmdq_registers {
    volatile open_cfw_cmdq_u32 *configuration;
    volatile open_cfw_cmdq_u32 *queue_address;
    volatile open_cfw_cmdq_u32 *current_index;
    volatile open_cfw_cmdq_u32 *end_index;
    volatile open_cfw_cmdq_u32 *pause;
    open_cfw_cmdq_u32 pause_index_mask;
    volatile open_cfw_cmdq_u32 *status;
    open_cfw_cmdq_u32 tip_mask;
    open_cfw_cmdq_u32 error_mask;
    open_cfw_cmdq_u32 paused_mask;
} open_cfw_cmdq_registers;

typedef struct open_cfw_cmdq_state {
    open_cfw_cmdq_u32 prefix;
    open_cfw_cmdq_u32 buffer_start;
    open_cfw_cmdq_u32 buffer_end;
    open_cfw_cmdq_u32 head;
    open_cfw_cmdq_u32 tail;
    open_cfw_cmdq_u32 next_tail;
    open_cfw_cmdq_u32 size;
    open_cfw_cmdq_u32 current_index;
    open_cfw_cmdq_u32 end_index;
    const open_cfw_cmdq_registers *registers;
    open_cfw_cmdq_u32 raw_sequence_start;
} open_cfw_cmdq_state;

#if !defined(OPEN_CFW_CMDQ_HOST_TEST)
_Static_assert(sizeof(open_cfw_cmdq_state) == 44U, "command-queue ABI changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_state, head) == 12U,
    "command-queue head offset changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_state, current_index) == 28U,
    "command-queue current-index offset changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_state, end_index) == 32U,
    "command-queue end-index offset changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_state, registers) == 36U,
    "command-queue register-table offset changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_registers, queue_address) == 4U,
    "command-queue address-register offset changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_registers, current_index) == 8U,
    "command-queue hardware-index offset changed");
#endif

#if defined(OPEN_CFW_CMDQ_HOST_TEST)
extern open_cfw_cmdq_u32 open_cfw_cmdq_host_critical_save(void);
extern void open_cfw_cmdq_host_critical_restore(open_cfw_cmdq_u32 token);
#define OPEN_CFW_CMDQ_CRITICAL_SAVE() open_cfw_cmdq_host_critical_save()
#define OPEN_CFW_CMDQ_CRITICAL_RESTORE(token) \
    open_cfw_cmdq_host_critical_restore(token)
#else
extern open_cfw_cmdq_u32 open_cfw_bootloader_critical_save_41b8ec(void);
#define OPEN_CFW_CMDQ_CRITICAL_SAVE() \
    open_cfw_bootloader_critical_save_41b8ec()
static __inline__ void
open_cfw_cmdq_critical_restore(open_cfw_cmdq_u32 token)
{
    __asm__ volatile("msr primask, %0" : : "r"(token) : "memory");
}
#define OPEN_CFW_CMDQ_CRITICAL_RESTORE(token) \
    open_cfw_cmdq_critical_restore(token)
#endif

__attribute__((used, noinline))
void
open_cfw_bootloader_cmdq_update_indices_427754(open_cfw_cmdq_state *queue)
{
    open_cfw_cmdq_u32 token = OPEN_CFW_CMDQ_CRITICAL_SAVE();
    open_cfw_cmdq_u32 hardware_current =
        *queue->registers->current_index & 0xFFU;

    queue->current_index = (queue->end_index & ~0xFFU) | hardware_current;
    if ((open_cfw_cmdq_s32)(queue->end_index - queue->current_index) < 0) {
        queue->current_index -= 0x100U;
    }
    queue->head = *queue->registers->queue_address;

    OPEN_CFW_CMDQ_CRITICAL_RESTORE(token);
}
