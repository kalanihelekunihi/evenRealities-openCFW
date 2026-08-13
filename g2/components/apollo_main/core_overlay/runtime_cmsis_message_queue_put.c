/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded adaptation of CMSIS-FreeRTOS v10.5.1 osMessageQueuePut() at
 * commit d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT8_TYPE__ open_cfw_cmsis_mq_put_uint8;
typedef __UINT32_TYPE__ open_cfw_cmsis_mq_put_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_mq_put_int32;
typedef __UINTPTR_TYPE__ open_cfw_cmsis_mq_put_uintptr;

enum {
    OPEN_CFW_CMSIS_MQ_PUT_OK = 0,
    OPEN_CFW_CMSIS_MQ_PUT_ERROR_TIMEOUT = -2,
    OPEN_CFW_CMSIS_MQ_PUT_ERROR_RESOURCE = -3,
    OPEN_CFW_CMSIS_MQ_PUT_ERROR_PARAMETER = -4
};

extern open_cfw_cmsis_mq_put_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_mq_put_int32
open_cfw_freertos_queue_generic_send_from_isr(
    void *queue,
    const void *item,
    open_cfw_cmsis_mq_put_int32 *higher_priority_task_woken,
    open_cfw_cmsis_mq_put_int32 copy_position
);
extern open_cfw_cmsis_mq_put_int32 open_cfw_freertos_queue_generic_send(
    void *queue,
    const void *item,
    open_cfw_cmsis_mq_put_uint32 timeout,
    open_cfw_cmsis_mq_put_int32 copy_position
);

#ifndef OPEN_CFW_CMSIS_MQ_PUT_PENDSV_SET
#define OPEN_CFW_CMSIS_MQ_PUT_PENDSV_SET() \
    (*(volatile open_cfw_cmsis_mq_put_uint32 *) \
        (open_cfw_cmsis_mq_put_uintptr)0xE000ED04U = 0x10000000U)
#endif

__attribute__((used, noinline))
open_cfw_cmsis_mq_put_int32 open_cfw_cmsis_message_queue_put(
    void *message_queue,
    const void *message,
    open_cfw_cmsis_mq_put_uint8 message_priority,
    open_cfw_cmsis_mq_put_uint32 timeout
)
{
    open_cfw_cmsis_mq_put_int32 yield;

    (void)message_priority;
    if (open_cfw_cmsis_irq_context() != 0U) {
        if (
            (message_queue == (void *)0) ||
            (message == (const void *)0) ||
            (timeout != 0U)
        ) {
            return OPEN_CFW_CMSIS_MQ_PUT_ERROR_PARAMETER;
        }
        yield = 0;
        if (
            open_cfw_freertos_queue_generic_send_from_isr(
                message_queue,
                message,
                &yield,
                0
            ) == 0
        ) {
            return OPEN_CFW_CMSIS_MQ_PUT_ERROR_RESOURCE;
        }
        if (yield != 0) {
            OPEN_CFW_CMSIS_MQ_PUT_PENDSV_SET();
        }
        return OPEN_CFW_CMSIS_MQ_PUT_OK;
    }

    if (
        (message_queue == (void *)0) ||
        (message == (const void *)0)
    ) {
        return OPEN_CFW_CMSIS_MQ_PUT_ERROR_PARAMETER;
    }
    if (
        open_cfw_freertos_queue_generic_send(
            message_queue,
            message,
            timeout,
            0
        ) == 0
    ) {
        if (timeout != 0U) {
            return OPEN_CFW_CMSIS_MQ_PUT_ERROR_TIMEOUT;
        }
        return OPEN_CFW_CMSIS_MQ_PUT_ERROR_RESOURCE;
    }
    return OPEN_CFW_CMSIS_MQ_PUT_OK;
}
