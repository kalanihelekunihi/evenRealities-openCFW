/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 * Production-intended, freestanding source boundary for osMessageQueueNew()
 * from the authenticated CMSIS-FreeRTOS v10.5.1 cmsis_os2.c at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 *
 * The upstream allocation and validation algorithm is retained exactly.
 * Focused disassembly of the official G2 2.2.6.10 image establishes the
 * selected configuration below: static and dynamic allocation are enabled,
 * the queue registry is disabled, StaticQueue_t is 0x50 bytes, and the
 * CMSIS message-queue attribute record uses its 32-bit layout.
 */

typedef unsigned int open_cfw_cmsis_uint32;
typedef signed int open_cfw_cmsis_int32;
typedef signed int open_cfw_cmsis_base_type;
typedef void *open_cfw_cmsis_queue_handle;
typedef void *open_cfw_cmsis_message_queue_id;

typedef struct {
    const char *name;
    open_cfw_cmsis_uint32 attr_bits;
    void *cb_mem;
    open_cfw_cmsis_uint32 cb_size;
    void *mq_mem;
    open_cfw_cmsis_uint32 mq_size;
} open_cfw_cmsis_message_queue_attr;

typedef struct {
    open_cfw_cmsis_uint32 words[0x50U / sizeof(open_cfw_cmsis_uint32)];
} open_cfw_cmsis_static_queue;

_Static_assert(
    sizeof(open_cfw_cmsis_uint32) == 4U,
    "CMSIS uint32_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_int32) == 4U,
    "CMSIS int32_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_base_type) == 4U,
    "FreeRTOS BaseType_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_static_queue) == 0x50U,
    "G2 StaticQueue_t ABI must remain 0x50 bytes"
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(
    sizeof(open_cfw_cmsis_message_queue_attr) == 0x18U,
    "G2 osMessageQueueAttr_t ABI must remain 24 bytes"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_message_queue_attr, name) == 0x00U,
    "G2 message-queue name offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_message_queue_attr, attr_bits) == 0x04U,
    "G2 message-queue attr_bits offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_message_queue_attr, cb_mem) == 0x08U,
    "G2 message-queue cb_mem offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_message_queue_attr, cb_size) == 0x0CU,
    "G2 message-queue cb_size offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_message_queue_attr, mq_mem) == 0x10U,
    "G2 message-queue mq_mem offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_message_queue_attr, mq_size) == 0x14U,
    "G2 message-queue mq_size offset drift"
);
#endif

/*
 * These aliases bind the exact upstream dependency names to source-owned
 * openCFW ABI functions. They are intentionally visible in the target ELF
 * relocation table.
 */
#define xTaskGetSchedulerState \
    open_cfw_freertos_task_get_scheduler_state
#define xQueueGenericCreateStatic \
    open_cfw_freertos_queue_generic_create_static
#define xQueueGenericCreate \
    open_cfw_freertos_queue_generic_create

extern open_cfw_cmsis_base_type xTaskGetSchedulerState(void);
extern open_cfw_cmsis_queue_handle xQueueGenericCreateStatic(
    open_cfw_cmsis_uint32 queue_length,
    open_cfw_cmsis_uint32 item_size,
    unsigned char *queue_storage,
    open_cfw_cmsis_static_queue *static_queue,
    unsigned char queue_type
);
extern open_cfw_cmsis_queue_handle xQueueGenericCreate(
    open_cfw_cmsis_uint32 queue_length,
    open_cfw_cmsis_uint32 item_size,
    unsigned char queue_type
);

#define configSUPPORT_STATIC_ALLOCATION 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configQUEUE_REGISTRY_SIZE 0

#define taskSCHEDULER_NOT_STARTED ((open_cfw_cmsis_base_type)1)
#define queueQUEUE_TYPE_BASE ((unsigned char)0U)

#define xQueueCreateStatic(queue_length, item_size, storage, static_queue) \
    xQueueGenericCreateStatic( \
        (queue_length), \
        (item_size), \
        (storage), \
        (static_queue), \
        queueQUEUE_TYPE_BASE \
    )
#define xQueueCreate(queue_length, item_size) \
    xQueueGenericCreate( \
        (queue_length), \
        (item_size), \
        queueQUEUE_TYPE_BASE \
    )

#if defined(OPEN_CFW_CMSIS_MESSAGE_QUEUE_HOST_TEST)
extern open_cfw_cmsis_uint32 open_cfw_cmsis_test_get_ipsr(void);
extern open_cfw_cmsis_uint32 open_cfw_cmsis_test_get_primask(void);
extern open_cfw_cmsis_uint32 open_cfw_cmsis_test_get_basepri(void);

#define OPEN_CFW_CMSIS_GET_IPSR() open_cfw_cmsis_test_get_ipsr()
#define OPEN_CFW_CMSIS_GET_PRIMASK() open_cfw_cmsis_test_get_primask()
#define OPEN_CFW_CMSIS_GET_BASEPRI() open_cfw_cmsis_test_get_basepri()
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

#define IS_IRQ_MODE() (OPEN_CFW_CMSIS_GET_IPSR() != 0U)
#define IS_IRQ_MASKED() \
    ((OPEN_CFW_CMSIS_GET_PRIMASK() != 0U) || \
     (OPEN_CFW_CMSIS_GET_BASEPRI() != 0U))

static inline open_cfw_cmsis_uint32 IRQ_Context(void)
{
    open_cfw_cmsis_uint32 irq;
    open_cfw_cmsis_base_type state;

    irq = 0U;

    if (IS_IRQ_MODE()) {
        irq = 1U;
    } else {
        state = xTaskGetSchedulerState();

        if (state != taskSCHEDULER_NOT_STARTED) {
            if (IS_IRQ_MASKED()) {
                irq = 1U;
            }
        }
    }

    return irq;
}

__attribute__((used, noinline))
open_cfw_cmsis_message_queue_id
open_cfw_cmsis_message_queue_new(
    open_cfw_cmsis_uint32 msg_count,
    open_cfw_cmsis_uint32 msg_size,
    const open_cfw_cmsis_message_queue_attr *attr
)
{
    open_cfw_cmsis_queue_handle hQueue;
    open_cfw_cmsis_int32 mem;

    hQueue = (open_cfw_cmsis_queue_handle)0;

    if ((IRQ_Context() == 0U) && (msg_count > 0U) && (msg_size > 0U)) {
        mem = -1;

        if (attr != (const open_cfw_cmsis_message_queue_attr *)0) {
            if (
                (attr->cb_mem != (void *)0) &&
                (attr->cb_size >= sizeof(open_cfw_cmsis_static_queue)) &&
                (attr->mq_mem != (void *)0) &&
                (attr->mq_size >= (msg_count * msg_size))
            ) {
                mem = 1;
            } else {
                if (
                    (attr->cb_mem == (void *)0) &&
                    (attr->cb_size == 0U) &&
                    (attr->mq_mem == (void *)0) &&
                    (attr->mq_size == 0U)
                ) {
                    mem = 0;
                }
            }
        } else {
            mem = 0;
        }

        if (mem == 1) {
#if configSUPPORT_STATIC_ALLOCATION == 1
            hQueue = xQueueCreateStatic(
                msg_count,
                msg_size,
                (unsigned char *)attr->mq_mem,
                (open_cfw_cmsis_static_queue *)attr->cb_mem
            );
#endif
        } else {
            if (mem == 0) {
#if configSUPPORT_DYNAMIC_ALLOCATION == 1
                hQueue = xQueueCreate(msg_count, msg_size);
#endif
            }
        }

#if configQUEUE_REGISTRY_SIZE > 0
#error "The recovered G2 osMessageQueueNew has no queue-registry branch"
#endif
    }

    return (open_cfw_cmsis_message_queue_id)hQueue;
}

