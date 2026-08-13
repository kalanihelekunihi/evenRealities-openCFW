/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding adapter for CMSIS-FreeRTOS v10.5.1
 * osSemaphoreAcquire() at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_sem_acquire_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_sem_acquire_int32;

enum {
    OPEN_CFW_CMSIS_SEM_ACQUIRE_OK = 0,
    OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_TIMEOUT = -2,
    OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_RESOURCE = -3,
    OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_PARAMETER = -4
};

extern open_cfw_cmsis_sem_acquire_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_sem_acquire_int32
open_cfw_freertos_queue_receive_from_isr(
    void *queue,
    void *buffer,
    open_cfw_cmsis_sem_acquire_int32 *higher_priority_task_woken
);
extern open_cfw_cmsis_sem_acquire_int32
open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    void *queue,
    open_cfw_cmsis_sem_acquire_uint32 timeout
);

#ifndef OPEN_CFW_CMSIS_SEM_ACQUIRE_PENDSV_SET
#define OPEN_CFW_CMSIS_SEM_ACQUIRE_PENDSV_SET() \
    (*(volatile open_cfw_cmsis_sem_acquire_uint32 *) \
        (__UINTPTR_TYPE__)0xE000ED04U = 0x10000000U)
#endif

__attribute__((used, noinline))
open_cfw_cmsis_sem_acquire_int32 open_cfw_cmsis_semaphore_acquire(
    void *semaphore,
    open_cfw_cmsis_sem_acquire_uint32 timeout
)
{
    open_cfw_cmsis_sem_acquire_int32 yield;

    if (semaphore == (void *)0) {
        return OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_PARAMETER;
    }
    if (open_cfw_cmsis_irq_context() != 0U) {
        if (timeout != 0U) {
            return OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_PARAMETER;
        }
        yield = 0;
        if (
            open_cfw_freertos_queue_receive_from_isr(
                semaphore,
                (void *)0,
                &yield
            ) == 0
        ) {
            return OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_RESOURCE;
        }
        if (yield != 0) {
            OPEN_CFW_CMSIS_SEM_ACQUIRE_PENDSV_SET();
        }
        return OPEN_CFW_CMSIS_SEM_ACQUIRE_OK;
    }
    if (
        open_cfw_freertos_queue_semaphore_take_upstream_candidate(
            semaphore,
            timeout
        ) == 0
    ) {
        if (timeout != 0U) {
            return OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_TIMEOUT;
        }
        return OPEN_CFW_CMSIS_SEM_ACQUIRE_ERROR_RESOURCE;
    }
    return OPEN_CFW_CMSIS_SEM_ACQUIRE_OK;
}
