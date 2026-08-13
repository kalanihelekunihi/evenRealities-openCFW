/* Copyright (c) 2013-2022 Arm Limited. SPDX-License-Identifier: Apache-2.0 */
typedef __UINT32_TYPE__ open_cfw_cmsis_kernel_lifecycle_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_kernel_lifecycle_int32;

enum {
    OPEN_CFW_CMSIS_LIFECYCLE_INACTIVE = 0,
    OPEN_CFW_CMSIS_LIFECYCLE_READY = 1,
    OPEN_CFW_CMSIS_LIFECYCLE_RUNNING = 2,
    OPEN_CFW_CMSIS_LIFECYCLE_ERROR = -1,
    OPEN_CFW_CMSIS_LIFECYCLE_ERROR_ISR = -6,
    OPEN_CFW_FREERTOS_LIFECYCLE_SCHEDULER_NOT_STARTED = 1
};

extern open_cfw_cmsis_kernel_lifecycle_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_kernel_lifecycle_int32
open_cfw_freertos_task_get_scheduler_state(void);
extern void open_cfw_retained_freertos_task_start_scheduler(void);

#ifndef OPEN_CFW_CMSIS_KERNEL_LIFECYCLE_STATE_WORD
#define OPEN_CFW_CMSIS_KERNEL_LIFECYCLE_STATE_WORD \
    (*(volatile open_cfw_cmsis_kernel_lifecycle_int32 *) \
        (__UINTPTR_TYPE__)0x20074384U)
#endif

#if !defined(OPEN_CFW_BUILD_CMSIS_KERNEL_START)
__attribute__((used,noinline))
open_cfw_cmsis_kernel_lifecycle_int32 open_cfw_cmsis_kernel_initialize(void)
{
    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_LIFECYCLE_ERROR_ISR;
    }
    if ((open_cfw_freertos_task_get_scheduler_state() ==
         OPEN_CFW_FREERTOS_LIFECYCLE_SCHEDULER_NOT_STARTED) &&
        (OPEN_CFW_CMSIS_KERNEL_LIFECYCLE_STATE_WORD ==
         OPEN_CFW_CMSIS_LIFECYCLE_INACTIVE)) {
        OPEN_CFW_CMSIS_KERNEL_LIFECYCLE_STATE_WORD =
            OPEN_CFW_CMSIS_LIFECYCLE_READY;
        return 0;
    }
    return OPEN_CFW_CMSIS_LIFECYCLE_ERROR;
}
#endif

#if !defined(OPEN_CFW_BUILD_CMSIS_KERNEL_INITIALIZE)
__attribute__((used,noinline))
open_cfw_cmsis_kernel_lifecycle_int32 open_cfw_cmsis_kernel_start(void)
{
    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_LIFECYCLE_ERROR_ISR;
    }
    if ((open_cfw_freertos_task_get_scheduler_state() ==
         OPEN_CFW_FREERTOS_LIFECYCLE_SCHEDULER_NOT_STARTED) &&
        (OPEN_CFW_CMSIS_KERNEL_LIFECYCLE_STATE_WORD ==
         OPEN_CFW_CMSIS_LIFECYCLE_READY)) {
        /* SVC_Setup is a two-byte no-op in the authenticated G2 build. */
        OPEN_CFW_CMSIS_KERNEL_LIFECYCLE_STATE_WORD =
            OPEN_CFW_CMSIS_LIFECYCLE_RUNNING;
        open_cfw_retained_freertos_task_start_scheduler();
        return 0;
    }
    return OPEN_CFW_CMSIS_LIFECYCLE_ERROR;
}
#endif
