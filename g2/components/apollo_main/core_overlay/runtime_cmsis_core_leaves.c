/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 * Bounded, freestanding ports of IRQ_Context(), osKernelGetTickCount(),
 * osThreadGetId(), and osMessageQueueGetCapacity() from CMSIS-FreeRTOS
 * v10.5.1 cmsis_os2.c at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53. The exact source blob first
 * appeared at commit 13acfbef7be85119fc6bc56832c455d4547d92c7.
 *
 * The official G2 Apollo-main entries are respectively:
 *
 *   [0x0044900E, 0x0044903C)  IRQ_Context
 *   [0x004490CC, 0x004490E2)  osKernelGetTickCount
 *   [0x004491AA, 0x004491B2)  osThreadGetId
 *   [0x00449BBC, 0x00449BC8)  osMessageQueueGetCapacity
 *
 * The ports call only FreeRTOS providers already owned by openCFW. The queue
 * capacity leaf reads the authenticated Queue_t uxLength word at +0x3C. None
 * of these functions dereferences the vendor-extended G2 TCB.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_base_type;
typedef void *open_cfw_cmsis_object_id;

enum {
    OPEN_CFW_CMSIS_TASK_SCHEDULER_NOT_STARTED = 1,
    OPEN_CFW_CMSIS_QUEUE_LENGTH_OFFSET = 0x3C
};

_Static_assert(sizeof(open_cfw_cmsis_uint32) == 4U,
    "G2 CMSIS uint32 width changed");

#if defined(OPEN_CFW_CMSIS_CORE_BUILD_LEAF) && \
    (defined(OPEN_CFW_CMSIS_CORE_LEAF_IRQ_CONTEXT) + \
        defined(OPEN_CFW_CMSIS_CORE_LEAF_KERNEL_TICK) + \
        defined(OPEN_CFW_CMSIS_CORE_LEAF_THREAD_ID) + \
        defined(OPEN_CFW_CMSIS_CORE_LEAF_QUEUE_CAPACITY)) != 1
#error "select exactly one CMSIS core leaf"
#endif

extern open_cfw_cmsis_base_type
open_cfw_freertos_task_get_scheduler_state(void);
extern open_cfw_cmsis_uint32
open_cfw_freertos_task_get_tick_count(void);
extern open_cfw_cmsis_uint32
open_cfw_freertos_task_get_tick_count_from_isr(void);
extern open_cfw_cmsis_object_id
open_cfw_freertos_task_get_current_task_handle(void);

#if !defined(OPEN_CFW_CMSIS_CORE_BUILD_LEAF) || \
    defined(OPEN_CFW_CMSIS_CORE_LEAF_IRQ_CONTEXT)
#if defined(OPEN_CFW_CMSIS_CORE_HOST_TEST)
extern open_cfw_cmsis_uint32 open_cfw_test_cmsis_get_ipsr(void);
extern open_cfw_cmsis_uint32 open_cfw_test_cmsis_get_primask(void);
extern open_cfw_cmsis_uint32 open_cfw_test_cmsis_get_basepri(void);
#define OPEN_CFW_CMSIS_GET_IPSR() open_cfw_test_cmsis_get_ipsr()
#define OPEN_CFW_CMSIS_GET_PRIMASK() open_cfw_test_cmsis_get_primask()
#define OPEN_CFW_CMSIS_GET_BASEPRI() open_cfw_test_cmsis_get_basepri()
#else
static __attribute__((always_inline)) inline open_cfw_cmsis_uint32
open_cfw_cmsis_get_ipsr(void)
{
    open_cfw_cmsis_uint32 result;
    __asm volatile ("mrs %0, ipsr" : "=r" (result));
    return result;
}

static __attribute__((always_inline)) inline open_cfw_cmsis_uint32
open_cfw_cmsis_get_primask(void)
{
    open_cfw_cmsis_uint32 result;
    __asm volatile ("mrs %0, primask" : "=r" (result));
    return result;
}

static __attribute__((always_inline)) inline open_cfw_cmsis_uint32
open_cfw_cmsis_get_basepri(void)
{
    open_cfw_cmsis_uint32 result;
    __asm volatile ("mrs %0, basepri" : "=r" (result));
    return result;
}

#define OPEN_CFW_CMSIS_GET_IPSR() open_cfw_cmsis_get_ipsr()
#define OPEN_CFW_CMSIS_GET_PRIMASK() open_cfw_cmsis_get_primask()
#define OPEN_CFW_CMSIS_GET_BASEPRI() open_cfw_cmsis_get_basepri()
#endif
#endif

#if !defined(OPEN_CFW_CMSIS_CORE_BUILD_LEAF) || \
    defined(OPEN_CFW_CMSIS_CORE_LEAF_IRQ_CONTEXT)
__attribute__((used, noinline))
open_cfw_cmsis_uint32 open_cfw_cmsis_irq_context(void)
{
    open_cfw_cmsis_uint32 irq = 0U;

    if (OPEN_CFW_CMSIS_GET_IPSR() != 0U) {
        irq = 1U;
    } else if (open_cfw_freertos_task_get_scheduler_state() !=
               OPEN_CFW_CMSIS_TASK_SCHEDULER_NOT_STARTED) {
        if ((OPEN_CFW_CMSIS_GET_PRIMASK() != 0U) ||
            (OPEN_CFW_CMSIS_GET_BASEPRI() != 0U)) {
            irq = 1U;
        }
    }

    return irq;
}
#endif

#if !defined(OPEN_CFW_CMSIS_CORE_BUILD_LEAF) || \
    defined(OPEN_CFW_CMSIS_CORE_LEAF_KERNEL_TICK)
extern open_cfw_cmsis_uint32 open_cfw_cmsis_irq_context(void);

__attribute__((used, noinline))
open_cfw_cmsis_uint32 open_cfw_cmsis_kernel_get_tick_count(void)
{
    open_cfw_cmsis_uint32 ticks;

    if (open_cfw_cmsis_irq_context() != 0U) {
        ticks = open_cfw_freertos_task_get_tick_count_from_isr();
    } else {
        ticks = open_cfw_freertos_task_get_tick_count();
    }

    return ticks;
}
#endif

#if !defined(OPEN_CFW_CMSIS_CORE_BUILD_LEAF) || \
    defined(OPEN_CFW_CMSIS_CORE_LEAF_THREAD_ID)
__attribute__((used, noinline))
open_cfw_cmsis_object_id open_cfw_cmsis_thread_get_id(void)
{
    return open_cfw_freertos_task_get_current_task_handle();
}
#endif

#if !defined(OPEN_CFW_CMSIS_CORE_BUILD_LEAF) || \
    defined(OPEN_CFW_CMSIS_CORE_LEAF_QUEUE_CAPACITY)
__attribute__((used, noinline))
open_cfw_cmsis_uint32
open_cfw_cmsis_message_queue_get_capacity(open_cfw_cmsis_object_id mq_id)
{
    const unsigned char *queue = (const unsigned char *)mq_id;
    open_cfw_cmsis_uint32 capacity = 0U;

    if (queue != (const unsigned char *)0) {
        capacity = *(const open_cfw_cmsis_uint32 *)(
            queue + OPEN_CFW_CMSIS_QUEUE_LENGTH_OFFSET);
    }

    return capacity;
}
#endif
