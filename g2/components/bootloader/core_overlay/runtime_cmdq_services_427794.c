/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2025, Ambiq Micro, Inc.
 *
 * Bounded Apollo510 am_hal_cmdq public-service adaptation for the G2 ABI.
 * The complete BSD-3-Clause terms are retained in this component's NOTICE.
 */

typedef __UINT8_TYPE__ open_cfw_cmdq_u8;
typedef __UINT32_TYPE__ open_cfw_cmdq_u32;
typedef __INT32_TYPE__ open_cfw_cmdq_s32;
typedef __UINTPTR_TYPE__ open_cfw_cmdq_uptr;
typedef _Bool open_cfw_cmdq_bool;

enum {
    OPEN_CFW_CMDQ_SUCCESS = 0U,
    OPEN_CFW_CMDQ_IN_USE = 3U,
    OPEN_CFW_CMDQ_OUT_OF_RANGE = 5U,
    OPEN_CFW_CMDQ_INVALID_ARG = 6U,
    OPEN_CFW_CMDQ_INVALID_OPERATION = 7U,
    OPEN_CFW_CMDQ_INVALID_HANDLE = 2U
};

enum {
    OPEN_CFW_CMDQ_MAGIC = 0x00CDCDCDU,
    OPEN_CFW_CMDQ_INITIALIZED = 0x01000000U,
    OPEN_CFW_CMDQ_ENABLED = 0x02000000U,
    OPEN_CFW_CMDQ_ENTRY_SIZE = 8U,
    OPEN_CFW_CMDQ_INTERFACE_COUNT = 12U,
    OPEN_CFW_CMDQ_SSRAM_BASE = 0x20080000U
};

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

typedef struct open_cfw_cmdq_config {
    open_cfw_cmdq_u32 size;
    open_cfw_cmdq_u32 buffer;
    open_cfw_cmdq_u32 priority;
} open_cfw_cmdq_config;

typedef struct open_cfw_cmdq_entry {
    open_cfw_cmdq_u32 address;
    open_cfw_cmdq_u32 value;
} open_cfw_cmdq_entry;

typedef struct open_cfw_cmdq_status {
    open_cfw_cmdq_u32 last_processed;
    open_cfw_cmdq_u32 last_posted;
    open_cfw_cmdq_u32 last_allocated;
    open_cfw_cmdq_bool transaction_in_progress;
    open_cfw_cmdq_bool paused;
    open_cfw_cmdq_bool error;
} open_cfw_cmdq_status;

#if !defined(OPEN_CFW_CMDQ_SERVICES_HOST_TEST)
_Static_assert(sizeof(open_cfw_cmdq_state) == 44U, "command-queue ABI changed");
_Static_assert(sizeof(open_cfw_cmdq_registers) == 40U,
    "command-queue register ABI changed");
_Static_assert(sizeof(open_cfw_cmdq_config) == 12U,
    "command-queue config ABI changed");
_Static_assert(sizeof(open_cfw_cmdq_entry) == 8U,
    "command-queue entry ABI changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_state, registers) == 36U,
    "command-queue register-table offset changed");
_Static_assert(__builtin_offsetof(open_cfw_cmdq_status, transaction_in_progress)
    == 12U, "command-queue status ABI changed");
#endif

#if defined(OPEN_CFW_CMDQ_SERVICES_HOST_TEST)
extern open_cfw_cmdq_state open_cfw_cmdq_host_states[OPEN_CFW_CMDQ_INTERFACE_COUNT];
extern open_cfw_cmdq_registers
    open_cfw_cmdq_host_registers[OPEN_CFW_CMDQ_INTERFACE_COUNT];
extern open_cfw_cmdq_entry *open_cfw_cmdq_host_resolve(open_cfw_cmdq_u32 address);
extern open_cfw_cmdq_u32 open_cfw_cmdq_host_register_address(
    const volatile open_cfw_cmdq_u32 *register_pointer);
extern void open_cfw_cmdq_host_dmb(void);
#define OPEN_CFW_CMDQ_STATES open_cfw_cmdq_host_states
#define OPEN_CFW_CMDQ_REGISTERS open_cfw_cmdq_host_registers
#define OPEN_CFW_CMDQ_RESOLVE(address) open_cfw_cmdq_host_resolve(address)
#define OPEN_CFW_CMDQ_REGISTER_ADDRESS(pointer) \
    open_cfw_cmdq_host_register_address(pointer)
#define OPEN_CFW_CMDQ_DMB() open_cfw_cmdq_host_dmb()
#else
#define OPEN_CFW_CMDQ_STATES \
    ((open_cfw_cmdq_state *)(open_cfw_cmdq_uptr)0x200262F0U)
#define OPEN_CFW_CMDQ_REGISTERS \
    ((const open_cfw_cmdq_registers *)(open_cfw_cmdq_uptr)0x00430880U)
#define OPEN_CFW_CMDQ_RESOLVE(address) \
    ((open_cfw_cmdq_entry *)(open_cfw_cmdq_uptr)(address))
#define OPEN_CFW_CMDQ_REGISTER_ADDRESS(pointer) \
    ((open_cfw_cmdq_u32)(open_cfw_cmdq_uptr)(pointer))
static __inline__ void open_cfw_cmdq_dmb(void)
{
    __asm__ volatile("dmb sy" : : : "memory");
}
#define OPEN_CFW_CMDQ_DMB() open_cfw_cmdq_dmb()
#endif

extern void open_cfw_bootloader_cmdq_update_indices_427754(
    open_cfw_cmdq_state *queue);

static __inline__ open_cfw_cmdq_bool
open_cfw_cmdq_valid(const open_cfw_cmdq_state *queue)
{
    return queue != (const open_cfw_cmdq_state *)0 &&
        (queue->prefix << 7U) ==
            (open_cfw_cmdq_u32)((OPEN_CFW_CMDQ_INITIALIZED |
                OPEN_CFW_CMDQ_MAGIC) << 7U);
}

static __inline__ open_cfw_cmdq_bool
open_cfw_cmdq_u32_smaller(open_cfw_cmdq_u32 left,
                          open_cfw_cmdq_u32 right)
{
    return (open_cfw_cmdq_s32)(left - right) < 0;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_init_427794(open_cfw_cmdq_u32 hardware_interface,
                                     const open_cfw_cmdq_config *config,
                                     void **handle_slot)
{
    open_cfw_cmdq_state *queue;
    open_cfw_cmdq_u32 start;

    if (hardware_interface >= OPEN_CFW_CMDQ_INTERFACE_COUNT) {
        return OPEN_CFW_CMDQ_OUT_OF_RANGE;
    }
    if (config == (const open_cfw_cmdq_config *)0 || config->buffer == 0U ||
        handle_slot == (void **)0 || config->size < 2U) {
        return OPEN_CFW_CMDQ_INVALID_ARG;
    }

    queue = &OPEN_CFW_CMDQ_STATES[hardware_interface];
    if ((queue->prefix & OPEN_CFW_CMDQ_INITIALIZED) != 0U) {
        return OPEN_CFW_CMDQ_INVALID_OPERATION;
    }

    start = config->buffer;
    queue->size = config->size * OPEN_CFW_CMDQ_ENTRY_SIZE;
    queue->tail = start;
    queue->next_tail = start;
    queue->head = start;
    queue->buffer_start = start;
    queue->buffer_end = start + queue->size;
    queue->prefix = (queue->prefix & 0xFC000000U) |
        OPEN_CFW_CMDQ_INITIALIZED | OPEN_CFW_CMDQ_MAGIC;
    queue->registers = &OPEN_CFW_CMDQ_REGISTERS[hardware_interface];
    queue->current_index = 0U;
    queue->end_index = 0U;
    *queue->registers->current_index = 0U;
    *queue->registers->end_index = 0U;
    *queue->registers->pause |= queue->registers->pause_index_mask;
    *queue->registers->queue_address = start;
    *queue->registers->configuration = (config->priority & 1U) << 1;
    *handle_slot = queue;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_enable_427878(void *handle)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if ((queue->prefix & OPEN_CFW_CMDQ_ENABLED) != 0U) {
        return OPEN_CFW_CMDQ_SUCCESS;
    }
    if (queue->buffer_end >= OPEN_CFW_CMDQ_SSRAM_BASE) {
        OPEN_CFW_CMDQ_DMB();
    }
    *queue->registers->configuration |= 1U;
    queue->prefix |= OPEN_CFW_CMDQ_ENABLED;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_disable_4278c8(void *handle)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if ((queue->prefix & OPEN_CFW_CMDQ_ENABLED) == 0U) {
        return OPEN_CFW_CMDQ_SUCCESS;
    }
    *queue->registers->configuration &= ~1U;
    queue->prefix &= ~OPEN_CFW_CMDQ_ENABLED;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_alloc_block_42790a(void *handle,
                                            open_cfw_cmdq_u32 command_count,
                                            open_cfw_cmdq_entry **block_slot,
                                            open_cfw_cmdq_u32 *index_slot)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;
    open_cfw_cmdq_u32 block_address;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if (block_slot == (open_cfw_cmdq_entry **)0 ||
        index_slot == (open_cfw_cmdq_u32 *)0) {
        return OPEN_CFW_CMDQ_INVALID_ARG;
    }
    if (queue->tail != queue->next_tail) {
        return OPEN_CFW_CMDQ_INVALID_OPERATION;
    }

    open_cfw_bootloader_cmdq_update_indices_427754(queue);
    if (open_cfw_cmdq_u32_smaller(queue->current_index + 254U,
                                  queue->end_index)) {
        return OPEN_CFW_CMDQ_OUT_OF_RANGE;
    }

    if (queue->tail >= queue->head) {
        if (queue->tail + (command_count + 2U) * OPEN_CFW_CMDQ_ENTRY_SIZE <=
            queue->buffer_end) {
            block_address = queue->tail;
        } else if (queue->buffer_start + (command_count + 1U) *
                       OPEN_CFW_CMDQ_ENTRY_SIZE < queue->head) {
            open_cfw_cmdq_entry *wrap = OPEN_CFW_CMDQ_RESOLVE(queue->tail);
            wrap->address = OPEN_CFW_CMDQ_REGISTER_ADDRESS(
                queue->registers->queue_address);
            wrap->value = queue->buffer_start;
            block_address = queue->buffer_start;
        } else {
            return OPEN_CFW_CMDQ_OUT_OF_RANGE;
        }
    } else if (queue->tail + (command_count + 1U) *
                   OPEN_CFW_CMDQ_ENTRY_SIZE < queue->head) {
        block_address = queue->tail;
    } else {
        return OPEN_CFW_CMDQ_OUT_OF_RANGE;
    }

    *block_slot = OPEN_CFW_CMDQ_RESOLVE(block_address);
    queue->end_index += 1U;
    *index_slot = queue->end_index;
    queue->next_tail = block_address + command_count *
        OPEN_CFW_CMDQ_ENTRY_SIZE;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_release_block_4279be(void *handle)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if (queue->tail == queue->next_tail) {
        return OPEN_CFW_CMDQ_INVALID_OPERATION;
    }
    queue->next_tail = queue->tail;
    queue->end_index -= 1U;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_post_block_4279f0(void *handle,
                                           open_cfw_cmdq_bool interrupt)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;
    open_cfw_cmdq_entry *entry;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if (queue->tail == queue->next_tail) {
        return OPEN_CFW_CMDQ_INVALID_OPERATION;
    }

    entry = OPEN_CFW_CMDQ_RESOLVE(queue->next_tail);
    entry->address = OPEN_CFW_CMDQ_REGISTER_ADDRESS(
        queue->registers->current_index) | (interrupt ? 1U : 0U);
    entry->value = queue->end_index;
    queue->tail = queue->next_tail + OPEN_CFW_CMDQ_ENTRY_SIZE;
    queue->next_tail = queue->tail;
    if (queue->buffer_end >= OPEN_CFW_CMDQ_SSRAM_BASE) {
        OPEN_CFW_CMDQ_DMB();
    }
    *queue->registers->end_index = queue->end_index & 0xFFU;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_get_status_427a56(void *handle,
                                           open_cfw_cmdq_status *result)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;
    open_cfw_cmdq_u32 hardware_status;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if (result == (open_cfw_cmdq_status *)0) {
        return OPEN_CFW_CMDQ_INVALID_ARG;
    }

    open_cfw_bootloader_cmdq_update_indices_427754(queue);
    result->last_processed = queue->current_index;
    result->last_allocated = queue->end_index;
    result->last_posted = queue->end_index -
        (queue->next_tail == queue->tail ? 0U : 1U);
    hardware_status = *queue->registers->status;
    result->transaction_in_progress =
        (hardware_status & queue->registers->tip_mask) != 0U;
    result->paused =
        (hardware_status & queue->registers->paused_mask) != 0U;
    result->error =
        (hardware_status & queue->registers->error_mask) != 0U;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_term_427ad6(void *handle, open_cfw_cmdq_bool force)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    open_cfw_bootloader_cmdq_update_indices_427754(queue);
    if (!force && queue->current_index != queue->end_index) {
        return OPEN_CFW_CMDQ_IN_USE;
    }
    queue->prefix &= ~OPEN_CFW_CMDQ_INITIALIZED;
    *queue->registers->configuration &= ~1U;
    *queue->registers->pause &= ~queue->registers->pause_index_mask;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_error_resume_427b38(void *handle)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;
    open_cfw_cmdq_u32 cursor;
    open_cfw_cmdq_u32 current_index_register;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if ((queue->prefix & OPEN_CFW_CMDQ_ENABLED) == 0U) {
        return OPEN_CFW_CMDQ_SUCCESS;
    }

    *queue->registers->configuration &= ~1U;
    cursor = *queue->registers->queue_address;
    current_index_register = OPEN_CFW_CMDQ_REGISTER_ADDRESS(
        queue->registers->current_index);
    for (;;) {
        open_cfw_cmdq_entry *entry = OPEN_CFW_CMDQ_RESOLVE(cursor);
        if ((entry->address & ~1U) == current_index_register) {
            entry->address = current_index_register;
            break;
        }
        if (entry->address == OPEN_CFW_CMDQ_REGISTER_ADDRESS(
                queue->registers->queue_address)) {
            cursor = entry->value;
        } else {
            cursor += OPEN_CFW_CMDQ_ENTRY_SIZE;
        }
    }
    *queue->registers->queue_address = cursor;
    queue->prefix &= ~OPEN_CFW_CMDQ_ENABLED;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_reset_427baa(void *handle)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if ((queue->prefix & OPEN_CFW_CMDQ_ENABLED) != 0U) {
        return OPEN_CFW_CMDQ_INVALID_OPERATION;
    }
    *queue->registers->configuration &= ~1U;
    queue->tail = queue->buffer_start;
    queue->next_tail = queue->buffer_start;
    queue->head = queue->buffer_start;
    queue->current_index = 0U;
    queue->end_index = 0U;
    *queue->registers->current_index = 0U;
    *queue->registers->end_index = 0U;
    *queue->registers->queue_address = queue->buffer_start;
    queue->prefix &= ~OPEN_CFW_CMDQ_ENABLED;
    return OPEN_CFW_CMDQ_SUCCESS;
}

__attribute__((used, noinline))
open_cfw_cmdq_u32
open_cfw_bootloader_cmdq_post_loop_block_427c12(void *handle,
                                                open_cfw_cmdq_bool interrupt)
{
    open_cfw_cmdq_state *queue = (open_cfw_cmdq_state *)handle;
    open_cfw_cmdq_entry *entry;

    if (!open_cfw_cmdq_valid(queue)) {
        return OPEN_CFW_CMDQ_INVALID_HANDLE;
    }
    if (queue->tail == queue->next_tail) {
        return OPEN_CFW_CMDQ_INVALID_OPERATION;
    }

    entry = OPEN_CFW_CMDQ_RESOLVE(queue->next_tail);
    entry->address = OPEN_CFW_CMDQ_REGISTER_ADDRESS(
        queue->registers->current_index);
    entry->value = 0U;
    entry += 1;
    entry->address = OPEN_CFW_CMDQ_REGISTER_ADDRESS(
        queue->registers->queue_address) | (interrupt ? 1U : 0U);
    entry->value = queue->buffer_start;
    queue->tail = queue->next_tail + 2U * OPEN_CFW_CMDQ_ENTRY_SIZE;
    queue->next_tail = queue->tail;
    if (queue->buffer_end >= OPEN_CFW_CMDQ_SSRAM_BASE) {
        OPEN_CFW_CMDQ_DMB();
    }
    *queue->registers->end_index = queue->end_index & 0xFFU;
    return OPEN_CFW_CMDQ_SUCCESS;
}
