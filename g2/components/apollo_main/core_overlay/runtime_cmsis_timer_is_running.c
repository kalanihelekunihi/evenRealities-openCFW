/* Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 * Bounded CMSIS-FreeRTOS v10.5.1 osTimerIsRunning candidate, commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53. Stock:
 * [0x00449522,0x0044953E). */

typedef __UINT32_TYPE__ open_cfw_cmsis_timer_uint32;
typedef const void *open_cfw_cmsis_timer_id;

extern open_cfw_cmsis_timer_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_timer_uint32
open_cfw_rtos_timer_is_active(open_cfw_cmsis_timer_id timer);

__attribute__((used, noinline))
open_cfw_cmsis_timer_uint32
open_cfw_cmsis_timer_is_running(open_cfw_cmsis_timer_id timer)
{
    if (open_cfw_cmsis_irq_context() != 0U ||
        timer == (open_cfw_cmsis_timer_id)0) {
        return 0U;
    }
    return open_cfw_rtos_timer_is_active(timer);
}
