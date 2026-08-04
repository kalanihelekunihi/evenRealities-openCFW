/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS internal timeout-state ABI for the Even Realities G2
 * Apollo-main image.  The recovered kernel-global words and TimeOut_t layout
 * remain explicit so the leaf is independently testable and relocation-free.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TIMEOUT_STATE_H
#define OPEN_CFW_RUNTIME_FREERTOS_TIMEOUT_STATE_H

typedef __INT32_TYPE__ open_cfw_freertos_timeout_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_timeout_tick_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_timeout_uintptr;

struct open_cfw_freertos_timeout_state {
    open_cfw_freertos_timeout_base_type overflow_count;
    open_cfw_freertos_timeout_tick_type time_on_entering;
};

enum {
    OPEN_CFW_FREERTOS_TIMEOUT_TICK_COUNT_ADDRESS = 0x20074A34U,
    OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_COUNT_ADDRESS = 0x20074A48U
};

_Static_assert(
    sizeof(open_cfw_freertos_timeout_base_type) == 4U,
    "G2 FreeRTOS BaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_timeout_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_timeout_state) == 8U,
    "G2 FreeRTOS TimeOut_t size changed"
);
_Static_assert(
    _Alignof(struct open_cfw_freertos_timeout_state) == 4U,
    "G2 FreeRTOS TimeOut_t alignment changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_timeout_state,
        overflow_count
    ) == 0U,
    "G2 FreeRTOS TimeOut_t overflow offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_timeout_state,
        time_on_entering
    ) == 4U,
    "G2 FreeRTOS TimeOut_t tick offset changed"
);

#ifndef OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_READ
#define OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_READ() \
    (*(volatile open_cfw_freertos_timeout_base_type *) \
        (open_cfw_freertos_timeout_uintptr) \
        OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_COUNT_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TIMEOUT_TICK_READ
#define OPEN_CFW_FREERTOS_TIMEOUT_TICK_READ() \
    (*(volatile open_cfw_freertos_timeout_tick_type *) \
        (open_cfw_freertos_timeout_uintptr) \
        OPEN_CFW_FREERTOS_TIMEOUT_TICK_COUNT_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_STORE
#define OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_STORE(timeout, value) \
    ((timeout)->overflow_count = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_TIMEOUT_TICK_STORE
#define OPEN_CFW_FREERTOS_TIMEOUT_TICK_STORE(timeout, value) \
    ((timeout)->time_on_entering = (value))
#endif

void open_cfw_freertos_task_internal_set_timeout_state(
    struct open_cfw_freertos_timeout_state *timeout
);

#endif
