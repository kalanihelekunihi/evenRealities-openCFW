/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS event-list reset ABI for the Even Realities G2
 * Apollo-main image. The recovered TCB layout and kernel-global seam remain
 * explicit so the leaf can be extracted as relocation-free target code.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_RESET_EVENT_ITEM_VALUE_H
#define OPEN_CFW_RUNTIME_FREERTOS_RESET_EVENT_ITEM_VALUE_H

typedef __UINT32_TYPE__ open_cfw_freertos_tick_type;
typedef __UINT32_TYPE__ open_cfw_freertos_ubase_type;

enum {
    OPEN_CFW_FREERTOS_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_EVENT_ITEM_VALUE_OFFSET = 0x18U,
    OPEN_CFW_FREERTOS_PRIORITY_OFFSET = 0x2CU,
    OPEN_CFW_FREERTOS_MAX_PRIORITIES = 56U
};

_Static_assert(
    sizeof(open_cfw_freertos_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);

struct open_cfw_freertos_event_tcb {
    unsigned char before_event_item_value[
        OPEN_CFW_FREERTOS_EVENT_ITEM_VALUE_OFFSET
    ];
    volatile open_cfw_freertos_tick_type event_item_value;
    unsigned char before_priority[
        OPEN_CFW_FREERTOS_PRIORITY_OFFSET
        - OPEN_CFW_FREERTOS_EVENT_ITEM_VALUE_OFFSET
        - sizeof(open_cfw_freertos_tick_type)
    ];
    volatile open_cfw_freertos_ubase_type priority;
};

_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_event_tcb,
        event_item_value
    ) == OPEN_CFW_FREERTOS_EVENT_ITEM_VALUE_OFFSET,
    "G2 FreeRTOS event-list item value offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_event_tcb,
        priority
    ) == OPEN_CFW_FREERTOS_PRIORITY_OFFSET,
    "G2 FreeRTOS priority offset changed"
);

#ifndef OPEN_CFW_FREERTOS_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_event_tcb * volatile *) \
        (__UINTPTR_TYPE__)OPEN_CFW_FREERTOS_CURRENT_TCB_ADDRESS)
#endif

open_cfw_freertos_tick_type
open_cfw_freertos_task_reset_event_item_value(void);

#endif
