/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS scheduler-suspension ABI for the Even Realities G2
 * Apollo-main image.  The recovered kernel-global word remains explicit so
 * the leaf is independently testable and relocation-free.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_SUSPEND_ALL_H
#define OPEN_CFW_RUNTIME_FREERTOS_SUSPEND_ALL_H

typedef __UINT32_TYPE__ open_cfw_freertos_suspend_all_ubase_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_suspend_all_uintptr;

enum {
    OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_ADDRESS = 0x20074A58U
};

_Static_assert(
    sizeof(open_cfw_freertos_suspend_all_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);

#ifndef OPEN_CFW_FREERTOS_SUSPEND_ALL_SOFTWARE_BARRIER
#define OPEN_CFW_FREERTOS_SUSPEND_ALL_SOFTWARE_BARRIER() \
    __asm__ __volatile__("" ::: "memory")
#endif

#ifndef OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_READ
#define OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_READ() \
    (*(volatile open_cfw_freertos_suspend_all_ubase_type *) \
        (open_cfw_freertos_suspend_all_uintptr) \
        OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_WRITE
#define OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_WRITE(value) \
    (*(volatile open_cfw_freertos_suspend_all_ubase_type *) \
        (open_cfw_freertos_suspend_all_uintptr) \
        OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_SUSPEND_ALL_MEMORY_BARRIER
#define OPEN_CFW_FREERTOS_SUSPEND_ALL_MEMORY_BARRIER() \
    __asm__ __volatile__("" ::: "memory")
#endif

void open_cfw_freertos_task_suspend_all(void);

#endif
