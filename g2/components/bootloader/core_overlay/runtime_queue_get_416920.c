/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded adaptation of CMSIS-FreeRTOS v10.5.1 osMessageQueueGet().
 */

typedef __UINT8_TYPE__ open_cfw_bootloader_queue_get_uint8;
typedef __UINT32_TYPE__ open_cfw_bootloader_queue_get_uint32;
typedef __INT32_TYPE__ open_cfw_bootloader_queue_get_int32;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_queue_get_uintptr;

enum {
    OPEN_CFW_BOOTLOADER_QUEUE_GET_OK = 0,
    OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_TIMEOUT = -2,
    OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_RESOURCE = -3,
    OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_PARAMETER = -4
};

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_queue_get_uint32
open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_GET_ISR_41A3B0
extern open_cfw_bootloader_queue_get_int32
open_cfw_bootloader_runtime_queue_get_isr_41a3b0(
    void *, void *, open_cfw_bootloader_queue_get_int32 *
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_GET_ISR_41A3B0(q,m,w) \
    open_cfw_bootloader_runtime_queue_get_isr_41a3b0((q),(m),(w))
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_GET_TASK_41A114
extern open_cfw_bootloader_queue_get_int32
open_cfw_bootloader_runtime_queue_get_task_41a114(
    void *, void *, open_cfw_bootloader_queue_get_uint32
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_GET_TASK_41A114(q,m,t) \
    open_cfw_bootloader_runtime_queue_get_task_41a114((q),(m),(t))
#endif

#ifndef OPEN_CFW_BOOTLOADER_QUEUE_GET_PENDSV_SET
#define OPEN_CFW_BOOTLOADER_QUEUE_GET_PENDSV_SET() \
    (*(volatile open_cfw_bootloader_queue_get_uint32 *) \
        (open_cfw_bootloader_queue_get_uintptr)0xE000ED04U = 0x10000000U)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_queue_get_int32
open_cfw_bootloader_runtime_queue_get_416920(
    void *queue,
    void *message,
    open_cfw_bootloader_queue_get_uint8 *priority,
    open_cfw_bootloader_queue_get_uint32 timeout
)
{
    open_cfw_bootloader_queue_get_int32 yield;

    (void)priority;
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        if (queue == (void *)0 || message == (void *)0 || timeout != 0U) {
            return OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_PARAMETER;
        }
        yield = 0;
        if (OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_GET_ISR_41A3B0(
                queue, message, &yield) != 1) {
            return OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_RESOURCE;
        }
        if (yield != 0) {
            OPEN_CFW_BOOTLOADER_QUEUE_GET_PENDSV_SET();
        }
        return OPEN_CFW_BOOTLOADER_QUEUE_GET_OK;
    }

    if (queue == (void *)0 || message == (void *)0) {
        return OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_PARAMETER;
    }
    if (OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_GET_TASK_41A114(
            queue, message, timeout) != 1) {
        return timeout != 0U
            ? OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_TIMEOUT
            : OPEN_CFW_BOOTLOADER_QUEUE_GET_ERROR_RESOURCE;
    }
    return OPEN_CFW_BOOTLOADER_QUEUE_GET_OK;
}
