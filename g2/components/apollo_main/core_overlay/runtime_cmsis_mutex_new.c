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
 * Production-intended, freestanding source boundary for osMutexNew() from
 * the authenticated CMSIS-FreeRTOS v10.5.1 cmsis_os2.c at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 *
 * The upstream allocation, attribute, and recursive-handle algorithm is
 * retained exactly. Focused disassembly of the official G2 2.2.6.10 image
 * establishes the selected configuration below: static and dynamic
 * allocation are enabled, recursive mutexes are enabled, the queue registry
 * is disabled, robust mutexes are rejected, StaticSemaphore_t is 0x50 bytes,
 * and the CMSIS mutex attribute record uses its 32-bit layout.
 */

typedef unsigned int open_cfw_cmsis_mutex_uint32;
typedef signed int open_cfw_cmsis_mutex_int32;
typedef signed int open_cfw_cmsis_mutex_base_type;
typedef __UINTPTR_TYPE__ open_cfw_cmsis_mutex_uintptr;
typedef void *open_cfw_cmsis_mutex_handle;
typedef void *open_cfw_cmsis_mutex_id;

typedef struct {
    const char *name;
    open_cfw_cmsis_mutex_uint32 attr_bits;
    void *cb_mem;
    open_cfw_cmsis_mutex_uint32 cb_size;
} open_cfw_cmsis_mutex_attr;

typedef struct {
    open_cfw_cmsis_mutex_uint32
        words[0x50U / sizeof(open_cfw_cmsis_mutex_uint32)];
} open_cfw_cmsis_static_semaphore;

_Static_assert(
    sizeof(open_cfw_cmsis_mutex_uint32) == 4U,
    "CMSIS uint32_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_mutex_int32) == 4U,
    "CMSIS int32_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_mutex_base_type) == 4U,
    "FreeRTOS BaseType_t ABI must remain 32 bits"
);
_Static_assert(
    sizeof(open_cfw_cmsis_static_semaphore) == 0x50U,
    "G2 StaticSemaphore_t ABI must remain 0x50 bytes"
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(
    sizeof(open_cfw_cmsis_mutex_attr) == 0x10U,
    "G2 osMutexAttr_t ABI must remain 16 bytes"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_mutex_attr, name) == 0x00U,
    "G2 mutex name offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_mutex_attr, attr_bits) == 0x04U,
    "G2 mutex attr_bits offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_mutex_attr, cb_mem) == 0x08U,
    "G2 mutex cb_mem offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_mutex_attr, cb_size) == 0x0CU,
    "G2 mutex cb_size offset drift"
);
#endif

/*
 * These aliases bind the exact upstream dependency names to source-owned
 * openCFW ABI functions. They are intentionally visible in the target ELF
 * relocation table.
 */
#define xTaskGetSchedulerState \
    open_cfw_freertos_task_get_scheduler_state
#define xQueueCreateMutexStatic \
    open_cfw_freertos_queue_create_mutex_static
#define xQueueCreateMutex \
    open_cfw_freertos_queue_create_mutex

extern open_cfw_cmsis_mutex_base_type xTaskGetSchedulerState(void);
extern open_cfw_cmsis_mutex_handle xQueueCreateMutexStatic(
    open_cfw_cmsis_mutex_uint32 queue_type,
    open_cfw_cmsis_static_semaphore *static_semaphore
);
extern open_cfw_cmsis_mutex_handle xQueueCreateMutex(
    unsigned char queue_type
);

#define configSUPPORT_STATIC_ALLOCATION 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configUSE_RECURSIVE_MUTEXES 1
#define configQUEUE_REGISTRY_SIZE 0

#define taskSCHEDULER_NOT_STARTED \
    ((open_cfw_cmsis_mutex_base_type)1)

#define osMutexRecursive ((open_cfw_cmsis_mutex_uint32)0x00000001U)
#define osMutexPrioInherit ((open_cfw_cmsis_mutex_uint32)0x00000002U)
#define osMutexRobust ((open_cfw_cmsis_mutex_uint32)0x00000008U)

#define queueQUEUE_TYPE_MUTEX \
    ((open_cfw_cmsis_mutex_uint32)1U)
#define queueQUEUE_TYPE_RECURSIVE_MUTEX \
    ((open_cfw_cmsis_mutex_uint32)4U)

#define xSemaphoreCreateRecursiveMutexStatic(static_semaphore) \
    xQueueCreateMutexStatic( \
        queueQUEUE_TYPE_RECURSIVE_MUTEX, \
        (static_semaphore) \
    )
#define xSemaphoreCreateMutexStatic(static_semaphore) \
    xQueueCreateMutexStatic( \
        queueQUEUE_TYPE_MUTEX, \
        (static_semaphore) \
    )
#define xSemaphoreCreateRecursiveMutex() \
    xQueueCreateMutex((unsigned char)queueQUEUE_TYPE_RECURSIVE_MUTEX)
#define xSemaphoreCreateMutex() \
    xQueueCreateMutex((unsigned char)queueQUEUE_TYPE_MUTEX)

#if defined(OPEN_CFW_CMSIS_MUTEX_HOST_TEST)
extern open_cfw_cmsis_mutex_uint32 open_cfw_cmsis_mutex_test_get_ipsr(void);
extern open_cfw_cmsis_mutex_uint32
open_cfw_cmsis_mutex_test_get_primask(void);
extern open_cfw_cmsis_mutex_uint32
open_cfw_cmsis_mutex_test_get_basepri(void);

#define OPEN_CFW_CMSIS_MUTEX_GET_IPSR() \
    open_cfw_cmsis_mutex_test_get_ipsr()
#define OPEN_CFW_CMSIS_MUTEX_GET_PRIMASK() \
    open_cfw_cmsis_mutex_test_get_primask()
#define OPEN_CFW_CMSIS_MUTEX_GET_BASEPRI() \
    open_cfw_cmsis_mutex_test_get_basepri()
#else
static __attribute__((always_inline)) inline
open_cfw_cmsis_mutex_uint32 open_cfw_cmsis_mutex_get_ipsr(void)
{
    open_cfw_cmsis_mutex_uint32 result;
    __asm volatile ("mrs %0, ipsr" : "=r" (result));
    return result;
}

static __attribute__((always_inline)) inline
open_cfw_cmsis_mutex_uint32 open_cfw_cmsis_mutex_get_primask(void)
{
    open_cfw_cmsis_mutex_uint32 result;
    __asm volatile ("mrs %0, primask" : "=r" (result));
    return result;
}

static __attribute__((always_inline)) inline
open_cfw_cmsis_mutex_uint32 open_cfw_cmsis_mutex_get_basepri(void)
{
    open_cfw_cmsis_mutex_uint32 result;
    __asm volatile ("mrs %0, basepri" : "=r" (result));
    return result;
}

#define OPEN_CFW_CMSIS_MUTEX_GET_IPSR() \
    open_cfw_cmsis_mutex_get_ipsr()
#define OPEN_CFW_CMSIS_MUTEX_GET_PRIMASK() \
    open_cfw_cmsis_mutex_get_primask()
#define OPEN_CFW_CMSIS_MUTEX_GET_BASEPRI() \
    open_cfw_cmsis_mutex_get_basepri()
#endif

#define OPEN_CFW_CMSIS_MUTEX_IS_IRQ_MODE() \
    (OPEN_CFW_CMSIS_MUTEX_GET_IPSR() != 0U)
#define OPEN_CFW_CMSIS_MUTEX_IS_IRQ_MASKED() \
    ((OPEN_CFW_CMSIS_MUTEX_GET_PRIMASK() != 0U) || \
     (OPEN_CFW_CMSIS_MUTEX_GET_BASEPRI() != 0U))

static inline open_cfw_cmsis_mutex_uint32
open_cfw_cmsis_mutex_irq_context(void)
{
    open_cfw_cmsis_mutex_uint32 irq;
    open_cfw_cmsis_mutex_base_type state;

    irq = 0U;

    if (OPEN_CFW_CMSIS_MUTEX_IS_IRQ_MODE()) {
        irq = 1U;
    } else {
        state = xTaskGetSchedulerState();

        if (state != taskSCHEDULER_NOT_STARTED) {
            if (OPEN_CFW_CMSIS_MUTEX_IS_IRQ_MASKED()) {
                irq = 1U;
            }
        }
    }

    return irq;
}

__attribute__((used, noinline))
open_cfw_cmsis_mutex_id
open_cfw_cmsis_mutex_new(const open_cfw_cmsis_mutex_attr *attr)
{
    open_cfw_cmsis_mutex_handle hMutex;
    open_cfw_cmsis_mutex_uint32 type;
    open_cfw_cmsis_mutex_uint32 rmtx;
    open_cfw_cmsis_mutex_int32 mem;

    hMutex = (open_cfw_cmsis_mutex_handle)0;

    if (open_cfw_cmsis_mutex_irq_context() == 0U) {
        if (attr != (const open_cfw_cmsis_mutex_attr *)0) {
            type = attr->attr_bits;
        } else {
            type = 0U;
        }

        if ((type & osMutexRecursive) == osMutexRecursive) {
            rmtx = 1U;
        } else {
            rmtx = 0U;
        }

        if ((type & osMutexRobust) != osMutexRobust) {
            mem = -1;

            if (attr != (const open_cfw_cmsis_mutex_attr *)0) {
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

            if (mem == 1) {
#if configSUPPORT_STATIC_ALLOCATION == 1
                if (rmtx != 0U) {
#if configUSE_RECURSIVE_MUTEXES == 1
                    hMutex = xSemaphoreCreateRecursiveMutexStatic(
                        (open_cfw_cmsis_static_semaphore *)attr->cb_mem
                    );
#endif
                } else {
                    hMutex = xSemaphoreCreateMutexStatic(
                        (open_cfw_cmsis_static_semaphore *)attr->cb_mem
                    );
                }
#endif
            } else {
                if (mem == 0) {
#if configSUPPORT_DYNAMIC_ALLOCATION == 1
                    if (rmtx != 0U) {
#if configUSE_RECURSIVE_MUTEXES == 1
                        hMutex = xSemaphoreCreateRecursiveMutex();
#endif
                    } else {
                        hMutex = xSemaphoreCreateMutex();
                    }
#endif
                }
            }

#if configQUEUE_REGISTRY_SIZE > 0
#error "The recovered G2 osMutexNew has no queue-registry branch"
#endif

            if (
                (hMutex != (open_cfw_cmsis_mutex_handle)0) &&
                (rmtx != 0U)
            ) {
                hMutex = (open_cfw_cmsis_mutex_handle)(
                    (open_cfw_cmsis_mutex_uintptr)hMutex |
                    (open_cfw_cmsis_mutex_uintptr)1U
                );
            }
        }
    }

    return (open_cfw_cmsis_mutex_id)hMutex;
}
