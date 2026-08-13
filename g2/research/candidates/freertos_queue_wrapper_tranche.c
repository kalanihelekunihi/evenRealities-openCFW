/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Isolated, non-production adaptations of xQueueCreateMutexStatic(),
 * xQueueCreateCountingSemaphoreStatic(), and
 * xQueueCreateCountingSemaphore() from queue.c at FreeRTOS-Kernel V10.5.1
 * commit def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 Apollo-main image owns the complete functions at
 * [0x004416F0, 0x00441710), [0x00441790, 0x004417C2), and
 * [0x004417C2, 0x004417EE), respectively.
 *
 * Queue creation and mutex initialisation close directly over project-prefixed
 * source interfaces. Only the invalid counting-semaphore dimensions retain the
 * reviewed official configASSERT fail-stop entry at 0x005FA0A4. This file is
 * deliberately not registered by the production overlay.
 */

typedef unsigned int open_cfw_queue_wrapper_ubase_type;
typedef unsigned char open_cfw_queue_wrapper_uint8;

struct open_cfw_queue_wrapper_control
{
    unsigned char before_messages_waiting[0x38];
    volatile open_cfw_queue_wrapper_ubase_type messages_waiting;
};

#if defined(__arm__)
_Static_assert(
    sizeof(void *) == 4U,
    "Apollo510 queue wrappers require 32-bit pointers");
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_wrapper_control,
        messages_waiting) == 0x38U,
    "G2 Queue_t uxMessagesWaiting offset changed");
#endif

extern struct open_cfw_queue_wrapper_control *
open_cfw_freertos_queue_generic_create_static(
    open_cfw_queue_wrapper_ubase_type length,
    open_cfw_queue_wrapper_ubase_type item_size,
    unsigned char *storage,
    struct open_cfw_queue_wrapper_control *static_queue,
    open_cfw_queue_wrapper_uint8 queue_type);

extern struct open_cfw_queue_wrapper_control *
open_cfw_freertos_queue_generic_create(
    open_cfw_queue_wrapper_ubase_type length,
    open_cfw_queue_wrapper_ubase_type item_size,
    open_cfw_queue_wrapper_uint8 queue_type);

extern void open_cfw_freertos_queue_initialise_mutex(
    struct open_cfw_queue_wrapper_control *queue);

#ifndef OPEN_CFW_FREERTOS_QUEUE_WRAPPER_ASSERT
typedef void (*open_cfw_queue_wrapper_assert_fail_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_WRAPPER_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            ((open_cfw_queue_wrapper_assert_fail_fn) \
                (__UINTPTR_TYPE__)0x005FA0A5U)(); \
            *(volatile open_cfw_queue_wrapper_ubase_type *) \
                (__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
            for (;;) { \
                __asm__ volatile("" ::: "memory"); \
            } \
        } \
    } while (0)
#endif

enum
{
    OPEN_CFW_QUEUE_WRAPPER_MUTEX_LENGTH = 1,
    OPEN_CFW_QUEUE_WRAPPER_SEMAPHORE_ITEM_SIZE = 0,
    OPEN_CFW_QUEUE_WRAPPER_COUNTING_SEMAPHORE_TYPE = 2
};

__attribute__((used, noinline))
struct open_cfw_queue_wrapper_control *
open_cfw_freertos_queue_create_mutex_static(
    open_cfw_queue_wrapper_ubase_type raw_queue_type,
    struct open_cfw_queue_wrapper_control *static_queue)
{
    struct open_cfw_queue_wrapper_control *new_queue;
    open_cfw_queue_wrapper_uint8 queue_type =
        (open_cfw_queue_wrapper_uint8)(raw_queue_type & 0xFFU);

    new_queue = open_cfw_freertos_queue_generic_create_static(
        OPEN_CFW_QUEUE_WRAPPER_MUTEX_LENGTH,
        OPEN_CFW_QUEUE_WRAPPER_SEMAPHORE_ITEM_SIZE,
        (unsigned char *)0,
        static_queue,
        queue_type);
    open_cfw_freertos_queue_initialise_mutex(new_queue);

    return new_queue;
}

__attribute__((used, noinline))
struct open_cfw_queue_wrapper_control *
open_cfw_freertos_queue_create_counting_semaphore_static(
    open_cfw_queue_wrapper_ubase_type maximum_count,
    open_cfw_queue_wrapper_ubase_type initial_count,
    struct open_cfw_queue_wrapper_control *static_queue)
{
    struct open_cfw_queue_wrapper_control *handle =
        (struct open_cfw_queue_wrapper_control *)0;

    if ((maximum_count != 0U) && (initial_count <= maximum_count))
    {
        handle = open_cfw_freertos_queue_generic_create_static(
            maximum_count,
            OPEN_CFW_QUEUE_WRAPPER_SEMAPHORE_ITEM_SIZE,
            (unsigned char *)0,
            static_queue,
            OPEN_CFW_QUEUE_WRAPPER_COUNTING_SEMAPHORE_TYPE);

        if (handle != (struct open_cfw_queue_wrapper_control *)0)
        {
            handle->messages_waiting = initial_count;
        }
    }
    else
    {
        OPEN_CFW_FREERTOS_QUEUE_WRAPPER_ASSERT(handle != 0);
    }

    return handle;
}

__attribute__((used, noinline))
struct open_cfw_queue_wrapper_control *
open_cfw_freertos_queue_create_counting_semaphore(
    open_cfw_queue_wrapper_ubase_type maximum_count,
    open_cfw_queue_wrapper_ubase_type initial_count)
{
    struct open_cfw_queue_wrapper_control *handle =
        (struct open_cfw_queue_wrapper_control *)0;

    if ((maximum_count != 0U) && (initial_count <= maximum_count))
    {
        handle = open_cfw_freertos_queue_generic_create(
            maximum_count,
            OPEN_CFW_QUEUE_WRAPPER_SEMAPHORE_ITEM_SIZE,
            OPEN_CFW_QUEUE_WRAPPER_COUNTING_SEMAPHORE_TYPE);

        if (handle != (struct open_cfw_queue_wrapper_control *)0)
        {
            handle->messages_waiting = initial_count;
        }
    }
    else
    {
        OPEN_CFW_FREERTOS_QUEUE_WRAPPER_ASSERT(handle != 0);
    }

    return handle;
}
