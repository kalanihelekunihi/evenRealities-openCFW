/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding adapter for CMSIS-FreeRTOS v10.5.1 osTimerNew()
 * and its private TimerCallback at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_timer_new_uint32;
typedef void *open_cfw_cmsis_timer_new_id;
typedef void (*open_cfw_cmsis_timer_new_function)(void *argument);
typedef void (*open_cfw_cmsis_timer_new_callback)(void *timer);

typedef struct {
    const char *name;
    open_cfw_cmsis_timer_new_uint32 attr_bits;
    void *cb_mem;
    open_cfw_cmsis_timer_new_uint32 cb_size;
} open_cfw_cmsis_timer_new_attr;

typedef struct {
    open_cfw_cmsis_timer_new_function function;
    void *argument;
} open_cfw_cmsis_timer_new_record;

enum {
    OPEN_CFW_CMSIS_TIMER_NEW_STATIC_TIMER_SIZE = 44U,
    OPEN_CFW_CMSIS_TIMER_NEW_RECORD_SIZE = 8U
};

extern open_cfw_cmsis_timer_new_uint32 open_cfw_cmsis_irq_context(void);
extern void *open_cfw_freertos_heap4_malloc(
    open_cfw_cmsis_timer_new_uint32 size
);
extern void open_cfw_freertos_heap4_free(void *memory);
extern void *open_cfw_rtos_timer_static_create(
    const char *name,
    open_cfw_cmsis_timer_new_uint32 period,
    open_cfw_cmsis_timer_new_uint32 reload,
    void *context,
    open_cfw_cmsis_timer_new_callback callback,
    void *buffer
);
extern void *open_cfw_rtos_timer_dynamic_create(
    const char *name,
    open_cfw_cmsis_timer_new_uint32 period,
    open_cfw_cmsis_timer_new_uint32 reload,
    void *context,
    open_cfw_cmsis_timer_new_callback callback
);
extern void *open_cfw_rtos_timer_get_context(const void *timer);

__attribute__((used, noinline))
void open_cfw_cmsis_timer_callback(void *timer)
{
    open_cfw_cmsis_timer_new_record *record =
        (open_cfw_cmsis_timer_new_record *)
        ((__UINTPTR_TYPE__)open_cfw_rtos_timer_get_context(timer) &
            ~(__UINTPTR_TYPE__)1U);

    if (record != (open_cfw_cmsis_timer_new_record *)0) {
        record->function(record->argument);
    }
}

__attribute__((used, noinline))
open_cfw_cmsis_timer_new_id open_cfw_cmsis_timer_new(
    open_cfw_cmsis_timer_new_function function,
    open_cfw_cmsis_timer_new_uint32 type,
    void *argument,
    const open_cfw_cmsis_timer_new_attr *attr
)
{
    const char *name = (const char *)0;
    open_cfw_cmsis_timer_new_record *record =
        (open_cfw_cmsis_timer_new_record *)0;
    open_cfw_cmsis_timer_new_uint32 record_dynamic = 0U;
    open_cfw_cmsis_timer_new_uint32 reload;
    int memory = -1;
    void *timer = (void *)0;

    if (
        (open_cfw_cmsis_irq_context() != 0U) ||
        (function == (open_cfw_cmsis_timer_new_function)0)
    ) {
        return (open_cfw_cmsis_timer_new_id)0;
    }

    if (
        (attr != (const open_cfw_cmsis_timer_new_attr *)0) &&
        (attr->cb_mem != (void *)0) &&
        (attr->cb_size >=
            (OPEN_CFW_CMSIS_TIMER_NEW_STATIC_TIMER_SIZE +
             OPEN_CFW_CMSIS_TIMER_NEW_RECORD_SIZE))
    ) {
        record = (open_cfw_cmsis_timer_new_record *)
            ((__UINTPTR_TYPE__)attr->cb_mem +
             OPEN_CFW_CMSIS_TIMER_NEW_STATIC_TIMER_SIZE);
    }
    if (record == (open_cfw_cmsis_timer_new_record *)0) {
        record = (open_cfw_cmsis_timer_new_record *)
            open_cfw_freertos_heap4_malloc(
                OPEN_CFW_CMSIS_TIMER_NEW_RECORD_SIZE
            );
        if (record != (open_cfw_cmsis_timer_new_record *)0) {
            record_dynamic = 1U;
        }
    }
    if (record == (open_cfw_cmsis_timer_new_record *)0) {
        return (open_cfw_cmsis_timer_new_id)0;
    }

    record->function = function;
    record->argument = argument;
    reload = (((unsigned char)type) == 0U) ? 0U : 1U;

    if (attr == (const open_cfw_cmsis_timer_new_attr *)0) {
        memory = 0;
    } else {
        name = attr->name;
        if (
            (attr->cb_mem != (void *)0) &&
            (attr->cb_size >= OPEN_CFW_CMSIS_TIMER_NEW_STATIC_TIMER_SIZE)
        ) {
            memory = 1;
        } else if (
            (attr->cb_mem == (void *)0) &&
            (attr->cb_size == 0U)
        ) {
            memory = 0;
        }
    }

    record = (open_cfw_cmsis_timer_new_record *)
        ((__UINTPTR_TYPE__)record | record_dynamic);
    if (memory == 1) {
        timer = open_cfw_rtos_timer_static_create(
            name,
            1U,
            reload,
            record,
            open_cfw_cmsis_timer_callback,
            attr->cb_mem
        );
    } else if (memory == 0) {
        timer = open_cfw_rtos_timer_dynamic_create(
            name,
            1U,
            reload,
            record,
            open_cfw_cmsis_timer_callback
        );
    }

    if (
        (timer == (void *)0) &&
        (record != (open_cfw_cmsis_timer_new_record *)0) &&
        (record_dynamic == 1U)
    ) {
        open_cfw_freertos_heap4_free(
            (void *)((__UINTPTR_TYPE__)record & ~(__UINTPTR_TYPE__)1U)
        );
    }
    return timer;
}
