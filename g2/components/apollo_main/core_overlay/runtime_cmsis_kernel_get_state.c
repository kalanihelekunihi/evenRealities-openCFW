/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding candidate for CMSIS-FreeRTOS v10.5.1
 * osKernelGetState() at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 *
 * Stock [0x0044906C,0x00449094) calls source-owned
 * xTaskGetSchedulerState() and, only while the scheduler is not started,
 * reads the CMSIS wrapper's KernelState word at 0x20074384.
 */

typedef __INT32_TYPE__ open_cfw_cmsis_kernel_state;
typedef __INT32_TYPE__ open_cfw_freertos_scheduler_state;

enum {
    OPEN_CFW_CMSIS_KERNEL_INACTIVE = 0,
    OPEN_CFW_CMSIS_KERNEL_READY = 1,
    OPEN_CFW_CMSIS_KERNEL_RUNNING = 2,
    OPEN_CFW_CMSIS_KERNEL_LOCKED = 3,
    OPEN_CFW_FREERTOS_SCHEDULER_SUSPENDED = 0,
    OPEN_CFW_FREERTOS_SCHEDULER_NOT_STARTED = 1,
    OPEN_CFW_FREERTOS_SCHEDULER_RUNNING = 2
};

extern open_cfw_freertos_scheduler_state
open_cfw_freertos_task_get_scheduler_state(void);

#ifndef OPEN_CFW_CMSIS_KERNEL_STATE_WORD
#define OPEN_CFW_CMSIS_KERNEL_STATE_WORD \
    (*(const volatile open_cfw_cmsis_kernel_state *)(__UINTPTR_TYPE__)0x20074384U)
#endif

__attribute__((used, noinline))
open_cfw_cmsis_kernel_state open_cfw_cmsis_kernel_get_state(void)
{
    open_cfw_freertos_scheduler_state scheduler_state =
        open_cfw_freertos_task_get_scheduler_state();

    if (scheduler_state == OPEN_CFW_FREERTOS_SCHEDULER_RUNNING) {
        return OPEN_CFW_CMSIS_KERNEL_RUNNING;
    }
    if (scheduler_state == OPEN_CFW_FREERTOS_SCHEDULER_SUSPENDED) {
        return OPEN_CFW_CMSIS_KERNEL_LOCKED;
    }
    if (OPEN_CFW_CMSIS_KERNEL_STATE_WORD == OPEN_CFW_CMSIS_KERNEL_READY) {
        return OPEN_CFW_CMSIS_KERNEL_READY;
    }
    return OPEN_CFW_CMSIS_KERNEL_INACTIVE;
}
