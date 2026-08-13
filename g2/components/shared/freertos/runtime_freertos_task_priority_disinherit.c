/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of xTaskPriorityDisinherit() at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. The official G2 body is
 * [0x0045596E,0x00455A12). The recovered one-word G2 TCB extension places
 * uxPriority, uxBasePriority, and uxMutexesHeld at +0x2C/+0x60/+0x64.
 */

typedef __INT32_TYPE__ open_cfw_freertos_disinherit_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_disinherit_ubase_type;
typedef __UINT8_TYPE__ open_cfw_freertos_disinherit_uint8;
typedef __UINTPTR_TYPE__ open_cfw_freertos_disinherit_uintptr;

enum {
    OPEN_CFW_FREERTOS_DISINHERIT_FALSE = 0,
    OPEN_CFW_FREERTOS_DISINHERIT_TRUE = 1,
    OPEN_CFW_FREERTOS_DISINHERIT_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_DISINHERIT_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_DISINHERIT_TOP_READY_ADDRESS = 0x20074A38U,
    OPEN_CFW_FREERTOS_DISINHERIT_READY_LISTS_ADDRESS = 0x2006A49CU,
    OPEN_CFW_FREERTOS_DISINHERIT_LIST_SIZE = 0x14U
};

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_CURRENT_TCB
#define OPEN_CFW_FREERTOS_DISINHERIT_CURRENT_TCB() \
    (*(void * volatile *)(open_cfw_freertos_disinherit_uintptr) \
        OPEN_CFW_FREERTOS_DISINHERIT_CURRENT_TCB_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_PRIORITY
#define OPEN_CFW_FREERTOS_DISINHERIT_PRIORITY(tcb) \
    (*(open_cfw_freertos_disinherit_ubase_type *) \
        ((open_cfw_freertos_disinherit_uint8 *)(tcb) + 0x2CU))
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_BASE_PRIORITY
#define OPEN_CFW_FREERTOS_DISINHERIT_BASE_PRIORITY(tcb) \
    (*(open_cfw_freertos_disinherit_ubase_type *) \
        ((open_cfw_freertos_disinherit_uint8 *)(tcb) + 0x60U))
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_MUTEXES_HELD
#define OPEN_CFW_FREERTOS_DISINHERIT_MUTEXES_HELD(tcb) \
    (*(open_cfw_freertos_disinherit_ubase_type *) \
        ((open_cfw_freertos_disinherit_uint8 *)(tcb) + 0x64U))
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_STATE_ITEM
#define OPEN_CFW_FREERTOS_DISINHERIT_STATE_ITEM(tcb) \
    ((void *)((open_cfw_freertos_disinherit_uint8 *)(tcb) + 0x04U))
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_EVENT_VALUE
#define OPEN_CFW_FREERTOS_DISINHERIT_EVENT_VALUE(tcb) \
    (*(open_cfw_freertos_disinherit_ubase_type *) \
        ((open_cfw_freertos_disinherit_uint8 *)(tcb) + 0x18U))
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_TOP_READY
#define OPEN_CFW_FREERTOS_DISINHERIT_TOP_READY() \
    (*(volatile open_cfw_freertos_disinherit_ubase_type *) \
        (open_cfw_freertos_disinherit_uintptr) \
        OPEN_CFW_FREERTOS_DISINHERIT_TOP_READY_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_READY_LIST
#define OPEN_CFW_FREERTOS_DISINHERIT_READY_LIST(priority) \
    ((void *)(open_cfw_freertos_disinherit_uintptr) \
        (OPEN_CFW_FREERTOS_DISINHERIT_READY_LISTS_ADDRESS + \
         ((priority) * OPEN_CFW_FREERTOS_DISINHERIT_LIST_SIZE)))
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_ASSERT
extern open_cfw_freertos_disinherit_ubase_type ulSetInterruptMask(void);
#define OPEN_CFW_FREERTOS_DISINHERIT_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)ulSetInterruptMask(); \
            *(volatile open_cfw_freertos_disinherit_ubase_type *) \
                (open_cfw_freertos_disinherit_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

extern open_cfw_freertos_disinherit_ubase_type
open_cfw_freertos_list_remove(void *item);
extern void open_cfw_freertos_list_insert_end(void *list, void *item);

__attribute__((used, noinline))
open_cfw_freertos_disinherit_base_type
open_cfw_freertos_task_priority_disinherit(void *mutex_holder)
{
    open_cfw_freertos_disinherit_base_type result =
        OPEN_CFW_FREERTOS_DISINHERIT_FALSE;

    if (mutex_holder != (void *)0) {
        open_cfw_freertos_disinherit_ubase_type priority;
        open_cfw_freertos_disinherit_ubase_type base_priority;

        OPEN_CFW_FREERTOS_DISINHERIT_ASSERT(
            mutex_holder == OPEN_CFW_FREERTOS_DISINHERIT_CURRENT_TCB()
        );
        OPEN_CFW_FREERTOS_DISINHERIT_ASSERT(
            OPEN_CFW_FREERTOS_DISINHERIT_MUTEXES_HELD(mutex_holder) != 0U
        );
        OPEN_CFW_FREERTOS_DISINHERIT_MUTEXES_HELD(mutex_holder) -= 1U;

        priority = OPEN_CFW_FREERTOS_DISINHERIT_PRIORITY(mutex_holder);
        base_priority =
            OPEN_CFW_FREERTOS_DISINHERIT_BASE_PRIORITY(mutex_holder);
        if (
            (priority != base_priority) &&
            (OPEN_CFW_FREERTOS_DISINHERIT_MUTEXES_HELD(mutex_holder) == 0U)
        ) {
            (void)open_cfw_freertos_list_remove(
                OPEN_CFW_FREERTOS_DISINHERIT_STATE_ITEM(mutex_holder)
            );
            OPEN_CFW_FREERTOS_DISINHERIT_PRIORITY(mutex_holder) =
                base_priority;
            OPEN_CFW_FREERTOS_DISINHERIT_EVENT_VALUE(mutex_holder) =
                OPEN_CFW_FREERTOS_DISINHERIT_MAX_PRIORITIES - base_priority;
            if (OPEN_CFW_FREERTOS_DISINHERIT_TOP_READY() < base_priority) {
                OPEN_CFW_FREERTOS_DISINHERIT_TOP_READY() = base_priority;
            }
            open_cfw_freertos_list_insert_end(
                OPEN_CFW_FREERTOS_DISINHERIT_READY_LIST(base_priority),
                OPEN_CFW_FREERTOS_DISINHERIT_STATE_ITEM(mutex_holder)
            );
            result = OPEN_CFW_FREERTOS_DISINHERIT_TRUE;
        }
    }
    return result;
}
