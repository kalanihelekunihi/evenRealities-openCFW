/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS timeout-check ABI for the Even Realities G2 Apollo-main
 * image.  The recovered RAM words and fixed providers remain explicit and
 * overridable so the production implementation can be exercised on a host
 * without changing its target ABI.  This header defines the registered
 * production leaf.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_CHECK_FOR_TIMEOUT_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_CHECK_FOR_TIMEOUT_H

typedef __INT32_TYPE__ open_cfw_freertos_check_timeout_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_check_timeout_tick_type;
typedef __UINT32_TYPE__ open_cfw_freertos_check_timeout_ubase_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_check_timeout_uintptr;

struct open_cfw_freertos_check_timeout_state {
    open_cfw_freertos_check_timeout_base_type overflow_count;
    open_cfw_freertos_check_timeout_tick_type time_on_entering;
};

enum {
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_FALSE = 0,
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TRUE = 1,
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT_MASK_ADDRESS = 0x005FA0A4U,
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ENTER_CRITICAL_ADDRESS = 0x004420D0U,
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET_ADDRESS = 0x00455556U,
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_EXIT_CRITICAL_ADDRESS = 0x004420E8U,
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TICK_COUNT_ADDRESS = 0x20074A34U,
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_OVERFLOW_COUNT_ADDRESS = 0x20074A48U
};

#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_MAX_DELAY __UINT32_MAX__

_Static_assert(
    sizeof(open_cfw_freertos_check_timeout_base_type) == 4U,
    "G2 FreeRTOS BaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_check_timeout_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_check_timeout_state) == 8U,
    "G2 FreeRTOS TimeOut_t size changed"
);
_Static_assert(
    _Alignof(struct open_cfw_freertos_check_timeout_state) == 4U,
    "G2 FreeRTOS TimeOut_t alignment changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_check_timeout_state,
        overflow_count
    ) == 0U,
    "G2 FreeRTOS TimeOut_t overflow offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_check_timeout_state,
        time_on_entering
    ) == 4U,
    "G2 FreeRTOS TimeOut_t tick offset changed"
);

typedef open_cfw_freertos_check_timeout_ubase_type
(*open_cfw_freertos_check_timeout_assert_mask_fn)(void);
typedef void (*open_cfw_freertos_check_timeout_critical_fn)(void);
typedef void (*open_cfw_freertos_check_timeout_internal_set_fn)(
    struct open_cfw_freertos_check_timeout_state *
);

#ifndef OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT_MASK
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT_MASK() \
    (((open_cfw_freertos_check_timeout_assert_mask_fn) \
        (open_cfw_freertos_check_timeout_uintptr) \
        (OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT_MASK_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT_MASK(); \
            *(volatile open_cfw_freertos_check_timeout_ubase_type *) \
                (open_cfw_freertos_check_timeout_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ENTER_CRITICAL
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ENTER_CRITICAL() \
    (((open_cfw_freertos_check_timeout_critical_fn) \
        (open_cfw_freertos_check_timeout_uintptr) \
        (OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ENTER_CRITICAL_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_CHECK_TIMEOUT_EXIT_CRITICAL
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_EXIT_CRITICAL() \
    (((open_cfw_freertos_check_timeout_critical_fn) \
        (open_cfw_freertos_check_timeout_uintptr) \
        (OPEN_CFW_FREERTOS_CHECK_TIMEOUT_EXIT_CRITICAL_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TICK_LOAD
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TICK_LOAD() \
    (*(volatile open_cfw_freertos_check_timeout_tick_type *) \
        (open_cfw_freertos_check_timeout_uintptr) \
        OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TICK_COUNT_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_CHECK_TIMEOUT_OVERFLOW_LOAD
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_OVERFLOW_LOAD() \
    (*(volatile open_cfw_freertos_check_timeout_base_type *) \
        (open_cfw_freertos_check_timeout_uintptr) \
        OPEN_CFW_FREERTOS_CHECK_TIMEOUT_OVERFLOW_COUNT_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET(timeout) \
    (((open_cfw_freertos_check_timeout_internal_set_fn) \
        (open_cfw_freertos_check_timeout_uintptr) \
        (OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET_ADDRESS | 1U)) \
            ((timeout)))
#endif

open_cfw_freertos_check_timeout_base_type
open_cfw_freertos_task_check_for_timeout(
    struct open_cfw_freertos_check_timeout_state *timeout,
    open_cfw_freertos_check_timeout_tick_type *ticks_to_wait
);

#endif
