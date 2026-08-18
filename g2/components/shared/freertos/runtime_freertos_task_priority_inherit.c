/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of xTaskPriorityInherit() at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. The official G2 body is
 * [0x004558CC,0x0045596E). The recovered one-word G2 TCB extension places
 * uxPriority, uxBasePriority at +0x2C/+0x60; the state list item is at +0x04
 * (its pxContainer at +0x14) and the event list item value is at +0x18.
 * The G2 kernel uses the generic ready-priority method, so
 * portRESET_READY_PRIORITY() is a no-op and prvAddTaskToReadyList() reduces to
 * the uxTopReadyPriority record plus a list insert-end. This mirrors the
 * already-landed sibling open_cfw_freertos_task_priority_disinherit.
 */

typedef __INT32_TYPE__ open_cfw_freertos_inherit_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_inherit_ubase_type;
typedef __UINT8_TYPE__ open_cfw_freertos_inherit_uint8;
typedef __UINTPTR_TYPE__ open_cfw_freertos_inherit_uintptr;

enum {
    OPEN_CFW_FREERTOS_INHERIT_FALSE = 0,
    OPEN_CFW_FREERTOS_INHERIT_TRUE = 1,
    OPEN_CFW_FREERTOS_INHERIT_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_INHERIT_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_INHERIT_TOP_READY_ADDRESS = 0x20074A38U,
    OPEN_CFW_FREERTOS_INHERIT_READY_LISTS_ADDRESS = 0x2006A49CU,
    OPEN_CFW_FREERTOS_INHERIT_LIST_SIZE = 0x14U
};

/* taskEVENT_LIST_ITEM_VALUE_IN_USE for the 32-bit-TickType G2 build. */
#define OPEN_CFW_FREERTOS_INHERIT_EVENT_IN_USE 0x80000000U

#ifndef OPEN_CFW_FREERTOS_INHERIT_CURRENT_TCB
#define OPEN_CFW_FREERTOS_INHERIT_CURRENT_TCB() \
    (*(void * volatile *)(open_cfw_freertos_inherit_uintptr) \
        OPEN_CFW_FREERTOS_INHERIT_CURRENT_TCB_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_INHERIT_PRIORITY
#define OPEN_CFW_FREERTOS_INHERIT_PRIORITY(tcb) \
    (*(open_cfw_freertos_inherit_ubase_type *) \
        ((open_cfw_freertos_inherit_uint8 *)(tcb) + 0x2CU))
#endif

#ifndef OPEN_CFW_FREERTOS_INHERIT_BASE_PRIORITY
#define OPEN_CFW_FREERTOS_INHERIT_BASE_PRIORITY(tcb) \
    (*(open_cfw_freertos_inherit_ubase_type *) \
        ((open_cfw_freertos_inherit_uint8 *)(tcb) + 0x60U))
#endif

#ifndef OPEN_CFW_FREERTOS_INHERIT_STATE_ITEM
#define OPEN_CFW_FREERTOS_INHERIT_STATE_ITEM(tcb) \
    ((void *)((open_cfw_freertos_inherit_uint8 *)(tcb) + 0x04U))
#endif

/* pxContainer of the state list item (ListItem_t + 0x10). */
#ifndef OPEN_CFW_FREERTOS_INHERIT_STATE_CONTAINER
#define OPEN_CFW_FREERTOS_INHERIT_STATE_CONTAINER(tcb) \
    (*(void * volatile *) \
        ((open_cfw_freertos_inherit_uint8 *)(tcb) + 0x14U))
#endif

#ifndef OPEN_CFW_FREERTOS_INHERIT_EVENT_VALUE
#define OPEN_CFW_FREERTOS_INHERIT_EVENT_VALUE(tcb) \
    (*(open_cfw_freertos_inherit_ubase_type *) \
        ((open_cfw_freertos_inherit_uint8 *)(tcb) + 0x18U))
#endif

#ifndef OPEN_CFW_FREERTOS_INHERIT_TOP_READY
#define OPEN_CFW_FREERTOS_INHERIT_TOP_READY() \
    (*(volatile open_cfw_freertos_inherit_ubase_type *) \
        (open_cfw_freertos_inherit_uintptr) \
        OPEN_CFW_FREERTOS_INHERIT_TOP_READY_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_INHERIT_READY_LIST
#define OPEN_CFW_FREERTOS_INHERIT_READY_LIST(priority) \
    ((void *)(open_cfw_freertos_inherit_uintptr) \
        (OPEN_CFW_FREERTOS_INHERIT_READY_LISTS_ADDRESS + \
         ((priority) * OPEN_CFW_FREERTOS_INHERIT_LIST_SIZE)))
#endif

extern open_cfw_freertos_inherit_ubase_type
open_cfw_freertos_list_remove(void *item);
extern void open_cfw_freertos_list_insert_end(void *list, void *item);

__attribute__((used, noinline))
open_cfw_freertos_inherit_base_type
open_cfw_freertos_task_priority_inherit(void *mutex_holder)
{
    open_cfw_freertos_inherit_base_type result =
        OPEN_CFW_FREERTOS_INHERIT_FALSE;

    if (mutex_holder != (void *)0) {
        open_cfw_freertos_inherit_ubase_type current_priority =
            OPEN_CFW_FREERTOS_INHERIT_PRIORITY(
                OPEN_CFW_FREERTOS_INHERIT_CURRENT_TCB());
        open_cfw_freertos_inherit_ubase_type hold_priority =
            OPEN_CFW_FREERTOS_INHERIT_PRIORITY(mutex_holder);

        if (hold_priority < current_priority) {
            if ((OPEN_CFW_FREERTOS_INHERIT_EVENT_VALUE(mutex_holder) &
                 OPEN_CFW_FREERTOS_INHERIT_EVENT_IN_USE) == 0U) {
                OPEN_CFW_FREERTOS_INHERIT_EVENT_VALUE(mutex_holder) =
                    OPEN_CFW_FREERTOS_INHERIT_MAX_PRIORITIES - current_priority;
            }

            if (OPEN_CFW_FREERTOS_INHERIT_STATE_CONTAINER(mutex_holder) ==
                OPEN_CFW_FREERTOS_INHERIT_READY_LIST(hold_priority)) {
                /* portRESET_READY_PRIORITY is a no-op for the generic method,
                 * so the removal result is discarded. */
                (void)open_cfw_freertos_list_remove(
                    OPEN_CFW_FREERTOS_INHERIT_STATE_ITEM(mutex_holder));
                OPEN_CFW_FREERTOS_INHERIT_PRIORITY(mutex_holder) =
                    current_priority;
                if (OPEN_CFW_FREERTOS_INHERIT_TOP_READY() < current_priority) {
                    OPEN_CFW_FREERTOS_INHERIT_TOP_READY() = current_priority;
                }
                open_cfw_freertos_list_insert_end(
                    OPEN_CFW_FREERTOS_INHERIT_READY_LIST(current_priority),
                    OPEN_CFW_FREERTOS_INHERIT_STATE_ITEM(mutex_holder));
            } else {
                OPEN_CFW_FREERTOS_INHERIT_PRIORITY(mutex_holder) =
                    current_priority;
            }
            result = OPEN_CFW_FREERTOS_INHERIT_TRUE;
        } else if (
            OPEN_CFW_FREERTOS_INHERIT_BASE_PRIORITY(mutex_holder) <
            current_priority) {
            result = OPEN_CFW_FREERTOS_INHERIT_TRUE;
        }
    }
    return result;
}
