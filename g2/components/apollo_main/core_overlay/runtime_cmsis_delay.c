/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 * Bounded CMSIS-FreeRTOS v10.5.1 osDelay() adaptation at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_delay_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_delay_int32;

enum {
    OPEN_CFW_CMSIS_DELAY_OK = 0,
    OPEN_CFW_CMSIS_DELAY_ERROR_ISR = -6
};

extern open_cfw_cmsis_delay_uint32 open_cfw_cmsis_irq_context(void);
extern void open_cfw_freertos_task_delay(open_cfw_cmsis_delay_uint32 ticks);

__attribute__((used, noinline))
open_cfw_cmsis_delay_int32 open_cfw_cmsis_delay(
    open_cfw_cmsis_delay_uint32 ticks
)
{
    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_DELAY_ERROR_ISR;
    }
    if (ticks != 0U) {
        open_cfw_freertos_task_delay(ticks);
    }
    return OPEN_CFW_CMSIS_DELAY_OK;
}
