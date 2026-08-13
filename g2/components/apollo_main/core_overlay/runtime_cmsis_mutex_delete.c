/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding candidate for CMSIS-FreeRTOS v10.5.1
 * osMutexDelete() at commit d213f261b5be6bb29a7cce8b84071706b72f4d53.
 * Stock [0x0044986E,0x0044989A) strips the recursive-mutex tag bit and calls
 * only source-owned IRQ_Context and vQueueDelete providers.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_mutex_delete_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_mutex_delete_status;
typedef void *open_cfw_cmsis_mutex_delete_id;

enum {
    OPEN_CFW_CMSIS_MUTEX_DELETE_OK = 0,
    OPEN_CFW_CMSIS_MUTEX_DELETE_ERROR_PARAMETER = -4,
    OPEN_CFW_CMSIS_MUTEX_DELETE_ERROR_ISR = -6
};

extern open_cfw_cmsis_mutex_delete_uint32 open_cfw_cmsis_irq_context(void);
extern void open_cfw_freertos_queue_delete(open_cfw_cmsis_mutex_delete_id queue);

__attribute__((used, noinline))
open_cfw_cmsis_mutex_delete_status
open_cfw_cmsis_mutex_delete(open_cfw_cmsis_mutex_delete_id mutex_id)
{
    open_cfw_cmsis_mutex_delete_id mutex =
        (open_cfw_cmsis_mutex_delete_id)((__UINTPTR_TYPE__)mutex_id &
            ~(__UINTPTR_TYPE__)1U);

    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_MUTEX_DELETE_ERROR_ISR;
    }
    if (mutex == (open_cfw_cmsis_mutex_delete_id)0) {
        return OPEN_CFW_CMSIS_MUTEX_DELETE_ERROR_PARAMETER;
    }
    open_cfw_freertos_queue_delete(mutex);
    return OPEN_CFW_CMSIS_MUTEX_DELETE_OK;
}
