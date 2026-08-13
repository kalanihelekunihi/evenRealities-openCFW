/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding candidates for the CMSIS-FreeRTOS v10.5.1
 * synchronization wrappers at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.  The authenticated G2 stock
 * bodies call only providers that are already source-owned by openCFW.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_sync_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_sync_int32;
typedef __INT32_TYPE__ open_cfw_cmsis_sync_status;
typedef void *open_cfw_cmsis_sync_id;

enum {
    OPEN_CFW_CMSIS_SYNC_OK = 0,
    OPEN_CFW_CMSIS_SYNC_ERROR_RESOURCE = -3,
    OPEN_CFW_CMSIS_SYNC_ERROR_PARAMETER = -4,
    OPEN_CFW_CMSIS_SYNC_ERROR_ISR = -6,
    OPEN_CFW_CMSIS_SYNC_ERROR_TIMEOUT = -2
};

extern open_cfw_cmsis_sync_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_sync_int32
open_cfw_freertos_queue_take_mutex_recursive(
    open_cfw_cmsis_sync_id mutex,
    open_cfw_cmsis_sync_uint32 timeout
);
extern open_cfw_cmsis_sync_int32
open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    open_cfw_cmsis_sync_id mutex,
    open_cfw_cmsis_sync_uint32 timeout
);
extern open_cfw_cmsis_sync_int32
open_cfw_freertos_queue_give_mutex_recursive(
    open_cfw_cmsis_sync_id mutex
);
extern open_cfw_cmsis_sync_int32 open_cfw_freertos_queue_generic_send(
    open_cfw_cmsis_sync_id queue,
    const void *item,
    open_cfw_cmsis_sync_uint32 timeout,
    open_cfw_cmsis_sync_int32 copy_position
);
extern open_cfw_cmsis_sync_int32 open_cfw_freertos_queue_give_from_isr(
    open_cfw_cmsis_sync_id queue,
    open_cfw_cmsis_sync_int32 *higher_priority_task_woken
);

#ifndef OPEN_CFW_CMSIS_SYNC_PENDSV_SET
#define OPEN_CFW_CMSIS_SYNC_PENDSV_SET() \
    (*(volatile open_cfw_cmsis_sync_uint32 *) \
        (__UINTPTR_TYPE__)0xE000ED04U = 0x10000000U)
#endif

static open_cfw_cmsis_sync_id
open_cfw_cmsis_sync_untag_mutex(open_cfw_cmsis_sync_id mutex_id)
{
    return (open_cfw_cmsis_sync_id)((__UINTPTR_TYPE__)mutex_id &
        ~(__UINTPTR_TYPE__)1U);
}

__attribute__((used, noinline))
open_cfw_cmsis_sync_status open_cfw_cmsis_mutex_acquire(
    open_cfw_cmsis_sync_id mutex_id,
    open_cfw_cmsis_sync_uint32 timeout
)
{
    open_cfw_cmsis_sync_id mutex =
        open_cfw_cmsis_sync_untag_mutex(mutex_id);
    open_cfw_cmsis_sync_int32 result;

    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_ISR;
    }
    if (mutex == (open_cfw_cmsis_sync_id)0) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_PARAMETER;
    }

    if (((__UINTPTR_TYPE__)mutex_id & 1U) != 0U) {
        result = open_cfw_freertos_queue_take_mutex_recursive(
            mutex,
            timeout
        );
    } else {
        result = open_cfw_freertos_queue_semaphore_take_upstream_candidate(
            mutex,
            timeout
        );
    }
    if (result != 0) {
        return OPEN_CFW_CMSIS_SYNC_OK;
    }
    if (timeout != 0U) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_TIMEOUT;
    }
    return OPEN_CFW_CMSIS_SYNC_ERROR_RESOURCE;
}

__attribute__((used, noinline))
open_cfw_cmsis_sync_status open_cfw_cmsis_mutex_release(
    open_cfw_cmsis_sync_id mutex_id
)
{
    open_cfw_cmsis_sync_id mutex =
        open_cfw_cmsis_sync_untag_mutex(mutex_id);
    open_cfw_cmsis_sync_int32 result;

    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_ISR;
    }
    if (mutex == (open_cfw_cmsis_sync_id)0) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_PARAMETER;
    }

    if (((__UINTPTR_TYPE__)mutex_id & 1U) != 0U) {
        result = open_cfw_freertos_queue_give_mutex_recursive(mutex);
    } else {
        result = open_cfw_freertos_queue_generic_send(mutex, 0, 0U, 0);
    }
    if (result == 0) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_RESOURCE;
    }
    return OPEN_CFW_CMSIS_SYNC_OK;
}

__attribute__((used, noinline))
open_cfw_cmsis_sync_status open_cfw_cmsis_semaphore_release(
    open_cfw_cmsis_sync_id semaphore_id
)
{
    open_cfw_cmsis_sync_int32 yield = 0;
    open_cfw_cmsis_sync_int32 result;

    if (semaphore_id == (open_cfw_cmsis_sync_id)0) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_PARAMETER;
    }

    if (open_cfw_cmsis_irq_context() != 0U) {
        result = open_cfw_freertos_queue_give_from_isr(
            semaphore_id,
            &yield
        );
        if (result == 0) {
            return OPEN_CFW_CMSIS_SYNC_ERROR_RESOURCE;
        }
        if (yield != 0) {
            OPEN_CFW_CMSIS_SYNC_PENDSV_SET();
        }
    } else if (
        open_cfw_freertos_queue_generic_send(
            semaphore_id,
            0,
            0U,
            0
        ) == 0
    ) {
        return OPEN_CFW_CMSIS_SYNC_ERROR_RESOURCE;
    }

    return OPEN_CFW_CMSIS_SYNC_OK;
}
