/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding adapters for CMSIS-FreeRTOS v10.5.1
 * osEventFlagsNew(), osEventFlagsSet(), osEventFlagsClear(), and
 * osEventFlagsWait() at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_event_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_event_int32;
typedef void *open_cfw_cmsis_event_id;

typedef struct {
    const char *name;
    open_cfw_cmsis_event_uint32 attr_bits;
    void *cb_mem;
    open_cfw_cmsis_event_uint32 cb_size;
} open_cfw_cmsis_event_attr;

enum {
    OPEN_CFW_CMSIS_EVENT_INVALID_BITS = 0xFF000000U,
    OPEN_CFW_CMSIS_EVENT_WAIT_ALL = 1U,
    OPEN_CFW_CMSIS_EVENT_NO_CLEAR = 2U,
    OPEN_CFW_CMSIS_EVENT_ERROR_TIMEOUT = -2,
    OPEN_CFW_CMSIS_EVENT_ERROR_RESOURCE = -3,
    OPEN_CFW_CMSIS_EVENT_ERROR_PARAMETER = -4,
    OPEN_CFW_CMSIS_EVENT_ERROR_ISR = -6,
    OPEN_CFW_CMSIS_EVENT_STATIC_CB_SIZE = 32U
};

extern open_cfw_cmsis_event_uint32 open_cfw_cmsis_irq_context(void);
extern void *open_cfw_rtos_event_group_static_create(void *buffer);
extern void *open_cfw_rtos_event_group_dynamic_create(void);
extern open_cfw_cmsis_event_uint32 open_cfw_rtos_event_group_set(
    void *group,
    open_cfw_cmsis_event_uint32 bits
);
extern open_cfw_cmsis_event_int32 open_cfw_rtos_event_group_set_from_isr(
    void *group,
    open_cfw_cmsis_event_uint32 bits,
    open_cfw_cmsis_event_int32 *higher_priority_task_woken
);
extern open_cfw_cmsis_event_uint32
open_cfw_rtos_event_group_get_bits_from_isr(void *group);
extern open_cfw_cmsis_event_uint32 open_cfw_rtos_event_group_clear(
    void *group,
    open_cfw_cmsis_event_uint32 bits
);
extern open_cfw_cmsis_event_int32 open_cfw_rtos_event_group_clear_from_isr(
    void *group,
    open_cfw_cmsis_event_uint32 bits
);
extern open_cfw_cmsis_event_uint32 open_cfw_rtos_event_group_wait(
    void *group,
    open_cfw_cmsis_event_uint32 bits,
    open_cfw_cmsis_event_int32 clear_on_exit,
    open_cfw_cmsis_event_int32 wait_all,
    open_cfw_cmsis_event_uint32 timeout
);

#ifndef OPEN_CFW_CMSIS_EVENT_PENDSV_SET
#define OPEN_CFW_CMSIS_EVENT_PENDSV_SET() \
    (*(volatile open_cfw_cmsis_event_uint32 *) \
        (__UINTPTR_TYPE__)0xE000ED04U = 0x10000000U)
#endif

__attribute__((used, noinline))
open_cfw_cmsis_event_id open_cfw_cmsis_event_flags_new(
    const open_cfw_cmsis_event_attr *attr
)
{
    open_cfw_cmsis_event_int32 memory = -1;

    if (open_cfw_cmsis_irq_context() != 0U) {
        return (open_cfw_cmsis_event_id)0;
    }
    if (attr == (const open_cfw_cmsis_event_attr *)0) {
        memory = 0;
    } else if (
        (attr->cb_mem != (void *)0) &&
        (attr->cb_size >= OPEN_CFW_CMSIS_EVENT_STATIC_CB_SIZE)
    ) {
        memory = 1;
    } else if (
        (attr->cb_mem == (void *)0) &&
        (attr->cb_size == 0U)
    ) {
        memory = 0;
    }

    if (memory == 1) {
        return open_cfw_rtos_event_group_static_create(attr->cb_mem);
    }
    if (memory == 0) {
        return open_cfw_rtos_event_group_dynamic_create();
    }
    return (open_cfw_cmsis_event_id)0;
}

__attribute__((used, noinline))
open_cfw_cmsis_event_uint32 open_cfw_cmsis_event_flags_set(
    open_cfw_cmsis_event_id event_flags,
    open_cfw_cmsis_event_uint32 flags
)
{
    open_cfw_cmsis_event_int32 yield = 0;
    open_cfw_cmsis_event_uint32 result;

    if (
        (event_flags == (open_cfw_cmsis_event_id)0) ||
        ((flags & OPEN_CFW_CMSIS_EVENT_INVALID_BITS) != 0U)
    ) {
        return (open_cfw_cmsis_event_uint32)
            OPEN_CFW_CMSIS_EVENT_ERROR_PARAMETER;
    }
    if (open_cfw_cmsis_irq_context() == 0U) {
        return open_cfw_rtos_event_group_set(event_flags, flags);
    }
    if (
        open_cfw_rtos_event_group_set_from_isr(
            event_flags,
            flags,
            &yield
        ) == 0
    ) {
        return (open_cfw_cmsis_event_uint32)
            OPEN_CFW_CMSIS_EVENT_ERROR_RESOURCE;
    }
    result = open_cfw_rtos_event_group_get_bits_from_isr(event_flags) | flags;
    if (yield != 0) {
        OPEN_CFW_CMSIS_EVENT_PENDSV_SET();
    }
    return result;
}

__attribute__((used, noinline))
open_cfw_cmsis_event_uint32 open_cfw_cmsis_event_flags_clear(
    open_cfw_cmsis_event_id event_flags,
    open_cfw_cmsis_event_uint32 flags
)
{
    open_cfw_cmsis_event_uint32 result;

    if (
        (event_flags == (open_cfw_cmsis_event_id)0) ||
        ((flags & OPEN_CFW_CMSIS_EVENT_INVALID_BITS) != 0U)
    ) {
        return (open_cfw_cmsis_event_uint32)
            OPEN_CFW_CMSIS_EVENT_ERROR_PARAMETER;
    }
    if (open_cfw_cmsis_irq_context() == 0U) {
        return open_cfw_rtos_event_group_clear(event_flags, flags);
    }
    result = open_cfw_rtos_event_group_get_bits_from_isr(event_flags);
    if (
        open_cfw_rtos_event_group_clear_from_isr(event_flags, flags) == 0
    ) {
        return (open_cfw_cmsis_event_uint32)
            OPEN_CFW_CMSIS_EVENT_ERROR_RESOURCE;
    }
    OPEN_CFW_CMSIS_EVENT_PENDSV_SET();
    return result;
}

__attribute__((used, noinline))
open_cfw_cmsis_event_uint32 open_cfw_cmsis_event_flags_wait(
    open_cfw_cmsis_event_id event_flags,
    open_cfw_cmsis_event_uint32 flags,
    open_cfw_cmsis_event_uint32 options,
    open_cfw_cmsis_event_uint32 timeout
)
{
    open_cfw_cmsis_event_int32 wait_all;
    open_cfw_cmsis_event_int32 clear_on_exit;
    open_cfw_cmsis_event_uint32 result;

    if (
        (event_flags == (open_cfw_cmsis_event_id)0) ||
        ((flags & OPEN_CFW_CMSIS_EVENT_INVALID_BITS) != 0U)
    ) {
        return (open_cfw_cmsis_event_uint32)
            OPEN_CFW_CMSIS_EVENT_ERROR_PARAMETER;
    }
    if (open_cfw_cmsis_irq_context() != 0U) {
        if (timeout == 0U) {
            return (open_cfw_cmsis_event_uint32)
                OPEN_CFW_CMSIS_EVENT_ERROR_ISR;
        }
        return (open_cfw_cmsis_event_uint32)
            OPEN_CFW_CMSIS_EVENT_ERROR_PARAMETER;
    }

    wait_all = ((options & OPEN_CFW_CMSIS_EVENT_WAIT_ALL) != 0U) ? 1 : 0;
    clear_on_exit =
        ((options & OPEN_CFW_CMSIS_EVENT_NO_CLEAR) != 0U) ? 0 : 1;
    result = open_cfw_rtos_event_group_wait(
        event_flags,
        flags,
        clear_on_exit,
        wait_all,
        timeout
    );

    if (wait_all != 0) {
        if ((result & flags) == flags) {
            return result;
        }
    } else if ((result & flags) != 0U) {
        return result;
    }
    if (timeout != 0U) {
        return (open_cfw_cmsis_event_uint32)
            OPEN_CFW_CMSIS_EVENT_ERROR_TIMEOUT;
    }
    return (open_cfw_cmsis_event_uint32)
        OPEN_CFW_CMSIS_EVENT_ERROR_RESOURCE;
}
