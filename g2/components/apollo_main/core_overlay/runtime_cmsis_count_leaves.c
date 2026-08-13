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
 * Bounded, freestanding ports of osSemaphoreGetCount() and
 * osMessageQueueGetCount() from CMSIS-FreeRTOS v10.5.1 cmsis_os2.c at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53. The exact source blob first
 * appeared at commit 13acfbef7be85119fc6bc56832c455d4547d92c7.
 *
 * The official G2 Apollo-main entries are:
 *
 *   [0x00449A0E, 0x00449A32)  osSemaphoreGetCount
 *   [0x00449BC8, 0x00449BEC)  osMessageQueueGetCount
 *
 * Both wrappers have the same dependency closure: the already source-owned
 * CMSIS IRQ classifier and the source-owned normal/ISR FreeRTOS queue-count
 * providers. SemaphoreHandle_t and QueueHandle_t share the Queue_t ABI.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_count_uint32;
typedef const void *open_cfw_cmsis_count_object_id;

_Static_assert(sizeof(open_cfw_cmsis_count_uint32) == 4U,
    "G2 CMSIS count width changed");

#if defined(OPEN_CFW_CMSIS_COUNT_BUILD_LEAF) && \
    (defined(OPEN_CFW_CMSIS_COUNT_LEAF_SEMAPHORE) + \
        defined(OPEN_CFW_CMSIS_COUNT_LEAF_MESSAGE_QUEUE)) != 1
#error "select exactly one CMSIS count leaf"
#endif

extern open_cfw_cmsis_count_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_count_uint32
open_cfw_freertos_queue_messages_waiting(open_cfw_cmsis_count_object_id queue);
extern open_cfw_cmsis_count_uint32
open_cfw_freertos_queue_messages_waiting_from_isr(
    open_cfw_cmsis_count_object_id queue
);

#if !defined(OPEN_CFW_CMSIS_COUNT_BUILD_LEAF) || \
    defined(OPEN_CFW_CMSIS_COUNT_LEAF_SEMAPHORE)
__attribute__((used, noinline))
open_cfw_cmsis_count_uint32
open_cfw_cmsis_semaphore_get_count(open_cfw_cmsis_count_object_id semaphore_id)
{
    open_cfw_cmsis_count_uint32 count = 0U;

    if (semaphore_id != (open_cfw_cmsis_count_object_id)0) {
        if (open_cfw_cmsis_irq_context() != 0U) {
            count = open_cfw_freertos_queue_messages_waiting_from_isr(
                semaphore_id);
        } else {
            count = open_cfw_freertos_queue_messages_waiting(semaphore_id);
        }
    }

    return count;
}
#endif

#if !defined(OPEN_CFW_CMSIS_COUNT_BUILD_LEAF) || \
    defined(OPEN_CFW_CMSIS_COUNT_LEAF_MESSAGE_QUEUE)
__attribute__((used, noinline))
open_cfw_cmsis_count_uint32
open_cfw_cmsis_message_queue_get_count(open_cfw_cmsis_count_object_id mq_id)
{
    open_cfw_cmsis_count_uint32 count = 0U;

    if (mq_id != (open_cfw_cmsis_count_object_id)0) {
        if (open_cfw_cmsis_irq_context() != 0U) {
            count = open_cfw_freertos_queue_messages_waiting_from_isr(mq_id);
        } else {
            count = open_cfw_freertos_queue_messages_waiting(mq_id);
        }
    }

    return count;
}
#endif
