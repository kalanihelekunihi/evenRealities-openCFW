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
 * Production-intended, freestanding source boundary for osSemaphoreNew()
 * from the authenticated CMSIS-FreeRTOS v10.5.1 cmsis_os2.c at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 *
 * The upstream allocation, validation, initialization, and cleanup
 * algorithm is retained exactly. Focused disassembly of the official G2
 * 2.2.6.10 image establishes the selected configuration below: static and
 * dynamic allocation are enabled, the queue registry is disabled,
 * StaticSemaphore_t is 0x50 bytes, and the CMSIS semaphore attribute record
 * uses its 32-bit layout.
 *
 * The production relocation closes cleanup through the source-owned
 * vQueueDelete implementation, which closes dynamic release through the
 * source-owned heap_4 allocator.
 */

typedef unsigned int open_cfw_cmsis_semaphore_uint32;
typedef signed int open_cfw_cmsis_semaphore_int32;
typedef signed int open_cfw_cmsis_semaphore_base_type;
typedef unsigned int open_cfw_cmsis_semaphore_tick_type;
typedef void *open_cfw_cmsis_semaphore_handle;
typedef void *open_cfw_cmsis_semaphore_id;

typedef struct {
    const char *name;
    open_cfw_cmsis_semaphore_uint32 attr_bits;
    void *cb_mem;
    open_cfw_cmsis_semaphore_uint32 cb_size;
} open_cfw_cmsis_semaphore_attr;

typedef struct {
    open_cfw_cmsis_semaphore_uint32
        words[0x50U / sizeof(open_cfw_cmsis_semaphore_uint32)];
} open_cfw_cmsis_static_semaphore;

_Static_assert(
    sizeof(open_cfw_cmsis_semaphore_uint32) == 4U,
    "CMSIS uint32_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_semaphore_int32) == 4U,
    "CMSIS int32_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_semaphore_base_type) == 4U,
    "FreeRTOS BaseType_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_static_semaphore) == 0x50U,
    "G2 StaticSemaphore_t ABI must remain 0x50 bytes"
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(
    sizeof(open_cfw_cmsis_semaphore_attr) == 0x10U,
    "G2 osSemaphoreAttr_t ABI must remain 16 bytes"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_semaphore_attr, name) == 0x00U,
    "G2 semaphore name offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_semaphore_attr, attr_bits) == 0x04U,
    "G2 semaphore attr_bits offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_semaphore_attr, cb_mem) == 0x08U,
    "G2 semaphore cb_mem offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_semaphore_attr, cb_size) == 0x0CU,
    "G2 semaphore cb_size offset drift"
);
#endif

/*
 * Preserve the exact upstream dependency names while binding every outgoing
 * target to the source-owned openCFW ABI.
 */
#define xTaskGetSchedulerState \
    open_cfw_freertos_task_get_scheduler_state
#define xQueueGenericCreateStatic \
    open_cfw_freertos_queue_generic_create_static
#define xQueueGenericCreate \
    open_cfw_freertos_queue_generic_create
#define xQueueGenericSend \
    open_cfw_freertos_queue_generic_send
#define vQueueDelete \
    open_cfw_freertos_queue_delete
#define xQueueCreateCountingSemaphoreStatic \
    open_cfw_freertos_queue_create_counting_semaphore_static
#define xQueueCreateCountingSemaphore \
    open_cfw_freertos_queue_create_counting_semaphore

extern open_cfw_cmsis_semaphore_base_type
xTaskGetSchedulerState(void);
extern open_cfw_cmsis_semaphore_handle xQueueGenericCreateStatic(
    open_cfw_cmsis_semaphore_uint32 queue_length,
    open_cfw_cmsis_semaphore_uint32 item_size,
    unsigned char *queue_storage,
    open_cfw_cmsis_static_semaphore *static_queue,
    unsigned char queue_type
);
extern open_cfw_cmsis_semaphore_handle xQueueGenericCreate(
    open_cfw_cmsis_semaphore_uint32 queue_length,
    open_cfw_cmsis_semaphore_uint32 item_size,
    unsigned char queue_type
);
extern open_cfw_cmsis_semaphore_base_type xQueueGenericSend(
    open_cfw_cmsis_semaphore_handle queue,
    const void *item,
    open_cfw_cmsis_semaphore_tick_type ticks_to_wait,
    open_cfw_cmsis_semaphore_base_type copy_position
);
extern void vQueueDelete(open_cfw_cmsis_semaphore_handle queue);
extern open_cfw_cmsis_semaphore_handle
xQueueCreateCountingSemaphoreStatic(
    open_cfw_cmsis_semaphore_uint32 maximum_count,
    open_cfw_cmsis_semaphore_uint32 initial_count,
    open_cfw_cmsis_static_semaphore *static_queue
);
extern open_cfw_cmsis_semaphore_handle xQueueCreateCountingSemaphore(
    open_cfw_cmsis_semaphore_uint32 maximum_count,
    open_cfw_cmsis_semaphore_uint32 initial_count
);

#define configSUPPORT_STATIC_ALLOCATION 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configQUEUE_REGISTRY_SIZE 0

#define taskSCHEDULER_NOT_STARTED \
    ((open_cfw_cmsis_semaphore_base_type)1)
#define queueQUEUE_TYPE_BINARY_SEMAPHORE ((unsigned char)3U)
#define queueSEND_TO_BACK ((open_cfw_cmsis_semaphore_base_type)0)
#define pdPASS ((open_cfw_cmsis_semaphore_base_type)1)

#define xSemaphoreCreateBinaryStatic(static_semaphore) \
    xQueueGenericCreateStatic( \
        1U, \
        0U, \
        (unsigned char *)0, \
        (static_semaphore), \
        queueQUEUE_TYPE_BINARY_SEMAPHORE \
    )
#define xSemaphoreCreateBinary() \
    xQueueGenericCreate(1U, 0U, queueQUEUE_TYPE_BINARY_SEMAPHORE)
#define xSemaphoreGive(semaphore) \
    xQueueGenericSend( \
        (semaphore), \
        (const void *)0, \
        0U, \
        queueSEND_TO_BACK \
    )
#define vSemaphoreDelete(semaphore) vQueueDelete((semaphore))
#define xSemaphoreCreateCountingStatic( \
    maximum_count, \
    initial_count, \
    static_semaphore \
) \
    xQueueCreateCountingSemaphoreStatic( \
        (maximum_count), \
        (initial_count), \
        (static_semaphore) \
    )
#define xSemaphoreCreateCounting(maximum_count, initial_count) \
    xQueueCreateCountingSemaphore((maximum_count), (initial_count))

#if defined(OPEN_CFW_CMSIS_SEMAPHORE_HOST_TEST)
extern open_cfw_cmsis_semaphore_uint32
open_cfw_cmsis_semaphore_test_get_ipsr(void);
extern open_cfw_cmsis_semaphore_uint32
open_cfw_cmsis_semaphore_test_get_primask(void);
extern open_cfw_cmsis_semaphore_uint32
open_cfw_cmsis_semaphore_test_get_basepri(void);

#define OPEN_CFW_CMSIS_SEMAPHORE_GET_IPSR() \
    open_cfw_cmsis_semaphore_test_get_ipsr()
#define OPEN_CFW_CMSIS_SEMAPHORE_GET_PRIMASK() \
    open_cfw_cmsis_semaphore_test_get_primask()
#define OPEN_CFW_CMSIS_SEMAPHORE_GET_BASEPRI() \
    open_cfw_cmsis_semaphore_test_get_basepri()
#else
static __attribute__((always_inline)) inline
open_cfw_cmsis_semaphore_uint32
open_cfw_cmsis_semaphore_get_ipsr(void)
{
    open_cfw_cmsis_semaphore_uint32 result;
    __asm volatile ("mrs %0, ipsr" : "=r" (result));
    return result;
}

static __attribute__((always_inline)) inline
open_cfw_cmsis_semaphore_uint32
open_cfw_cmsis_semaphore_get_primask(void)
{
    open_cfw_cmsis_semaphore_uint32 result;
    __asm volatile ("mrs %0, primask" : "=r" (result));
    return result;
}

static __attribute__((always_inline)) inline
open_cfw_cmsis_semaphore_uint32
open_cfw_cmsis_semaphore_get_basepri(void)
{
    open_cfw_cmsis_semaphore_uint32 result;
    __asm volatile ("mrs %0, basepri" : "=r" (result));
    return result;
}

#define OPEN_CFW_CMSIS_SEMAPHORE_GET_IPSR() \
    open_cfw_cmsis_semaphore_get_ipsr()
#define OPEN_CFW_CMSIS_SEMAPHORE_GET_PRIMASK() \
    open_cfw_cmsis_semaphore_get_primask()
#define OPEN_CFW_CMSIS_SEMAPHORE_GET_BASEPRI() \
    open_cfw_cmsis_semaphore_get_basepri()
#endif

#define OPEN_CFW_CMSIS_SEMAPHORE_IS_IRQ_MODE() \
    (OPEN_CFW_CMSIS_SEMAPHORE_GET_IPSR() != 0U)
#define OPEN_CFW_CMSIS_SEMAPHORE_IS_IRQ_MASKED() \
    ((OPEN_CFW_CMSIS_SEMAPHORE_GET_PRIMASK() != 0U) || \
     (OPEN_CFW_CMSIS_SEMAPHORE_GET_BASEPRI() != 0U))

static inline open_cfw_cmsis_semaphore_uint32
open_cfw_cmsis_semaphore_irq_context(void)
{
    open_cfw_cmsis_semaphore_uint32 irq;
    open_cfw_cmsis_semaphore_base_type state;

    irq = 0U;

    if (OPEN_CFW_CMSIS_SEMAPHORE_IS_IRQ_MODE()) {
        irq = 1U;
    } else {
        state = xTaskGetSchedulerState();

        if (state != taskSCHEDULER_NOT_STARTED) {
            if (OPEN_CFW_CMSIS_SEMAPHORE_IS_IRQ_MASKED()) {
                irq = 1U;
            }
        }
    }

    return irq;
}

__attribute__((used, noinline))
open_cfw_cmsis_semaphore_id
open_cfw_cmsis_semaphore_new(
    open_cfw_cmsis_semaphore_uint32 max_count,
    open_cfw_cmsis_semaphore_uint32 initial_count,
    const open_cfw_cmsis_semaphore_attr *attr
)
{
    open_cfw_cmsis_semaphore_handle hSemaphore;
    open_cfw_cmsis_semaphore_int32 mem;

    hSemaphore = (open_cfw_cmsis_semaphore_handle)0;

    if (
        (open_cfw_cmsis_semaphore_irq_context() == 0U) &&
        (max_count > 0U) &&
        (initial_count <= max_count)
    ) {
        mem = -1;

        if (attr != (const open_cfw_cmsis_semaphore_attr *)0) {
            if (
                (attr->cb_mem != (void *)0) &&
                (attr->cb_size >=
                 sizeof(open_cfw_cmsis_static_semaphore))
            ) {
                mem = 1;
            } else {
                if (
                    (attr->cb_mem == (void *)0) &&
                    (attr->cb_size == 0U)
                ) {
                    mem = 0;
                }
            }
        } else {
            mem = 0;
        }

        if (mem != -1) {
            if (max_count == 1U) {
                if (mem == 1) {
#if configSUPPORT_STATIC_ALLOCATION == 1
                    hSemaphore = xSemaphoreCreateBinaryStatic(
                        (open_cfw_cmsis_static_semaphore *)attr->cb_mem
                    );
#endif
                } else {
#if configSUPPORT_DYNAMIC_ALLOCATION == 1
                    hSemaphore = xSemaphoreCreateBinary();
#endif
                }

                if (
                    (hSemaphore != (open_cfw_cmsis_semaphore_handle)0) &&
                    (initial_count != 0U)
                ) {
                    if (xSemaphoreGive(hSemaphore) != pdPASS) {
                        vSemaphoreDelete(hSemaphore);
                        hSemaphore =
                            (open_cfw_cmsis_semaphore_handle)0;
                    }
                }
            } else {
                if (mem == 1) {
#if configSUPPORT_STATIC_ALLOCATION == 1
                    hSemaphore = xSemaphoreCreateCountingStatic(
                        max_count,
                        initial_count,
                        (open_cfw_cmsis_static_semaphore *)attr->cb_mem
                    );
#endif
                } else {
#if configSUPPORT_DYNAMIC_ALLOCATION == 1
                    hSemaphore = xSemaphoreCreateCounting(
                        max_count,
                        initial_count
                    );
#endif
                }
            }

#if configQUEUE_REGISTRY_SIZE > 0
#error "The recovered G2 osSemaphoreNew has no queue-registry branch"
#endif
        }
    }

    return (open_cfw_cmsis_semaphore_id)hSemaphore;
}
