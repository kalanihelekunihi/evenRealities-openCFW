/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of vTaskPriorityDisinheritAfterTimeout() at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. The official G2 body is
 * [0x00455A1C,0x00455ACA). The reviewed apple-clang codegen fully inlines
 * prvAddTaskToReadyList() and vListInsertEnd() at this call site (only the
 * external uxListRemove() survives as a call), so the ready-list insertion is
 * expressed here over the recovered G2 List_t/ListItem_t layout rather than as
 * a call into the source-owned list_insert_end leaf. The recovered one-word G2
 * TCB extension places uxPriority, xEventListItem value, uxBasePriority, and
 * uxMutexesHeld at +0x2C/+0x18/+0x60/+0x64; xStateListItem begins at +0x04.
 */

typedef __INT32_TYPE__ open_cfw_freertos_disinherit_after_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_disinherit_after_ubase_type;
typedef __UINT8_TYPE__ open_cfw_freertos_disinherit_after_uint8;
typedef __UINTPTR_TYPE__ open_cfw_freertos_disinherit_after_uintptr;

enum {
    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_ONLY_ONE_MUTEX_HELD = 1U,
    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_EVENT_VALUE_IN_USE = 0x80000000UL,
    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_TOP_READY_ADDRESS = 0x20074A38U,
    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_READY_LISTS_ADDRESS = 0x2006A49CU
};

typedef struct open_cfw_freertos_disinherit_after_list_item {
    open_cfw_freertos_disinherit_after_ubase_type xItemValue;
    struct open_cfw_freertos_disinherit_after_list_item *pxNext;
    struct open_cfw_freertos_disinherit_after_list_item *pxPrevious;
    void *pvOwner;
    void *pvContainer;
} open_cfw_freertos_disinherit_after_list_item_t;

typedef struct open_cfw_freertos_disinherit_after_mini_list_item {
    open_cfw_freertos_disinherit_after_ubase_type xItemValue;
    open_cfw_freertos_disinherit_after_list_item_t *pxNext;
    open_cfw_freertos_disinherit_after_list_item_t *pxPrevious;
} open_cfw_freertos_disinherit_after_mini_list_item_t;

typedef struct open_cfw_freertos_disinherit_after_list {
    open_cfw_freertos_disinherit_after_ubase_type uxNumberOfItems;
    open_cfw_freertos_disinherit_after_list_item_t *pxIndex;
    open_cfw_freertos_disinherit_after_mini_list_item_t xListEnd;
} open_cfw_freertos_disinherit_after_list_t;

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_PRIORITY(tcb) \
    (*(open_cfw_freertos_disinherit_after_ubase_type *) \
        ((open_cfw_freertos_disinherit_after_uint8 *)(tcb) + 0x2CU))

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_BASE_PRIORITY(tcb) \
    (*(open_cfw_freertos_disinherit_after_ubase_type *) \
        ((open_cfw_freertos_disinherit_after_uint8 *)(tcb) + 0x60U))

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_MUTEXES_HELD(tcb) \
    (*(open_cfw_freertos_disinherit_after_ubase_type *) \
        ((open_cfw_freertos_disinherit_after_uint8 *)(tcb) + 0x64U))

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_EVENT_VALUE(tcb) \
    (*(open_cfw_freertos_disinherit_after_ubase_type *) \
        ((open_cfw_freertos_disinherit_after_uint8 *)(tcb) + 0x18U))

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_STATE_ITEM(tcb) \
    ((open_cfw_freertos_disinherit_after_list_item_t *) \
        ((open_cfw_freertos_disinherit_after_uint8 *)(tcb) + 0x04U))

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_CURRENT_TCB() \
    (*(void * volatile *)(open_cfw_freertos_disinherit_after_uintptr) \
        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_CURRENT_TCB_ADDRESS)

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_TOP_READY() \
    (*(volatile open_cfw_freertos_disinherit_after_ubase_type *) \
        (open_cfw_freertos_disinherit_after_uintptr) \
        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_TOP_READY_ADDRESS)

#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_READY_LISTS() \
    ((open_cfw_freertos_disinherit_after_list_t *) \
        (open_cfw_freertos_disinherit_after_uintptr) \
        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_READY_LISTS_ADDRESS)

extern open_cfw_freertos_disinherit_after_ubase_type ulSetInterruptMask(void);
#define OPEN_CFW_FREERTOS_DISINHERIT_AFTER_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)ulSetInterruptMask(); \
            *(volatile open_cfw_freertos_disinherit_after_ubase_type *) \
                (open_cfw_freertos_disinherit_after_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)

extern open_cfw_freertos_disinherit_after_ubase_type
open_cfw_freertos_list_remove(void *item);

__attribute__((used, noinline))
void
open_cfw_freertos_task_priority_disinherit_after_timeout(
    void *mutex_holder,
    open_cfw_freertos_disinherit_after_ubase_type highest_priority_waiting_task)
{
    void *const tcb = mutex_holder;
    const open_cfw_freertos_disinherit_after_ubase_type only_one_mutex_held =
        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_ONLY_ONE_MUTEX_HELD;

    if (mutex_holder != (void *)0) {
        open_cfw_freertos_disinherit_after_ubase_type priority_used_on_entry;
        open_cfw_freertos_disinherit_after_ubase_type priority_to_use;

        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_ASSERT(
            OPEN_CFW_FREERTOS_DISINHERIT_AFTER_MUTEXES_HELD(tcb)
        );

        if (OPEN_CFW_FREERTOS_DISINHERIT_AFTER_BASE_PRIORITY(tcb) <
            highest_priority_waiting_task) {
            priority_to_use = highest_priority_waiting_task;
        } else {
            priority_to_use =
                OPEN_CFW_FREERTOS_DISINHERIT_AFTER_BASE_PRIORITY(tcb);
        }

        if (OPEN_CFW_FREERTOS_DISINHERIT_AFTER_PRIORITY(tcb) != priority_to_use) {
            if (OPEN_CFW_FREERTOS_DISINHERIT_AFTER_MUTEXES_HELD(tcb) ==
                only_one_mutex_held) {
                OPEN_CFW_FREERTOS_DISINHERIT_AFTER_ASSERT(
                    tcb != OPEN_CFW_FREERTOS_DISINHERIT_AFTER_CURRENT_TCB()
                );

                priority_used_on_entry =
                    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_PRIORITY(tcb);
                OPEN_CFW_FREERTOS_DISINHERIT_AFTER_PRIORITY(tcb) =
                    priority_to_use;

                if ((OPEN_CFW_FREERTOS_DISINHERIT_AFTER_EVENT_VALUE(tcb) &
                     OPEN_CFW_FREERTOS_DISINHERIT_AFTER_EVENT_VALUE_IN_USE) ==
                    0UL) {
                    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_EVENT_VALUE(tcb) =
                        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_MAX_PRIORITIES -
                        priority_to_use;
                }

                open_cfw_freertos_disinherit_after_list_t *const ready_lists =
                    OPEN_CFW_FREERTOS_DISINHERIT_AFTER_READY_LISTS();
                open_cfw_freertos_disinherit_after_list_item_t *const
                    state_item =
                        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_STATE_ITEM(tcb);

                if (state_item->pvContainer ==
                    &ready_lists[priority_used_on_entry]) {
                    (void)open_cfw_freertos_list_remove(state_item);

                    if (OPEN_CFW_FREERTOS_DISINHERIT_AFTER_TOP_READY() <
                        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_PRIORITY(tcb)) {
                        OPEN_CFW_FREERTOS_DISINHERIT_AFTER_TOP_READY() =
                            OPEN_CFW_FREERTOS_DISINHERIT_AFTER_PRIORITY(tcb);
                    }

                    open_cfw_freertos_disinherit_after_list_t *const list =
                        &ready_lists
                            [OPEN_CFW_FREERTOS_DISINHERIT_AFTER_PRIORITY(tcb)];
                    open_cfw_freertos_disinherit_after_list_item_t *const index =
                        list->pxIndex;

                    state_item->pxNext = index;
                    state_item->pxPrevious = index->pxPrevious;
                    index->pxPrevious->pxNext = state_item;
                    index->pxPrevious = state_item;
                    state_item->pvContainer = list;
                    list->uxNumberOfItems++;
                }
            }
        }
    }
}
