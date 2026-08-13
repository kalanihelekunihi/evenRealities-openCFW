/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS mutex-held-count ABI for the Even Realities G2 Apollo-main
 * image.  The recovered current-task and TCB-field seams remain explicit so
 * the source-owned leaf is independently testable and relocation-free.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_MUTEX_HELD_H
#define OPEN_CFW_RUNTIME_FREERTOS_MUTEX_HELD_H

typedef __UINT32_TYPE__ open_cfw_freertos_mutex_held_ubase_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_mutex_held_uintptr;
typedef void *open_cfw_freertos_mutex_held_task_handle;

enum {
    OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_MUTEX_HELD_COUNT_OFFSET = 0x64U,
    OPEN_CFW_FREERTOS_MUTEX_HELD_CONFIG_USE_MUTEXES = 1
};

_Static_assert(
    sizeof(open_cfw_freertos_mutex_held_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);

#ifndef OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_READ
#define OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_READ() \
    (*(volatile open_cfw_freertos_mutex_held_uintptr *) \
        (open_cfw_freertos_mutex_held_uintptr) \
        OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_MUTEX_HELD_COUNT
#define OPEN_CFW_FREERTOS_MUTEX_HELD_COUNT(tcb) \
    (*(open_cfw_freertos_mutex_held_ubase_type *) \
        ((open_cfw_freertos_mutex_held_uintptr)(tcb) + \
            OPEN_CFW_FREERTOS_MUTEX_HELD_COUNT_OFFSET))
#endif

#ifndef OPEN_CFW_FREERTOS_MUTEX_HELD_INCREMENT
#define OPEN_CFW_FREERTOS_MUTEX_HELD_INCREMENT(tcb) \
    do { \
        OPEN_CFW_FREERTOS_MUTEX_HELD_COUNT(tcb)++; \
    } while (0)
#endif

open_cfw_freertos_mutex_held_task_handle
open_cfw_freertos_task_increment_mutex_held_count(void);

#endif
