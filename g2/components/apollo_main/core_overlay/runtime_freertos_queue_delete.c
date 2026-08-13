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
 * Bounded, freestanding adaptation of the exact vQueueDelete() algorithm from
 * queue.c at authenticated FreeRTOS-Kernel V10.5.1 commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * Focused disassembly of the official G2 2.2.6.10 Apollo-main image proves:
 *
 * - configSUPPORT_DYNAMIC_ALLOCATION == 1;
 * - configSUPPORT_STATIC_ALLOCATION == 1;
 * - configQUEUE_REGISTRY_SIZE == 0;
 * - traceQUEUE_DELETE() and mtCOVERAGE_TEST_MARKER() emit no code;
 * - Queue_t.ucStaticallyAllocated is the byte at offset 0x46; and
 * - the assertion and allocator calls are the only external dependencies.
 *
 * The assertion path binds directly to the source-owned ulSetInterruptMask().
 * Dynamic deletion binds to the future source-owned heap_4 vPortFree adapter.
 */

typedef unsigned int open_cfw_queue_delete_ubase_type;
typedef unsigned char open_cfw_queue_delete_uint8;
typedef open_cfw_queue_delete_uint8 uint8_t;

typedef struct open_cfw_queue_delete_control
{
    unsigned char before_statically_allocated[0x46];
    open_cfw_queue_delete_uint8 ucStaticallyAllocated;
    unsigned char after_statically_allocated[0x09];
} open_cfw_queue_delete_control;

typedef open_cfw_queue_delete_control *QueueHandle_t;
typedef open_cfw_queue_delete_control Queue_t;

#if defined(__arm__) && \
    !defined(OPEN_CFW_FREERTOS_QUEUE_DELETE_SKIP_ABI_ASSERTS)
_Static_assert(
    sizeof(void *) == 4U,
    "Apollo510 queue deletion requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_queue_delete_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t view changed");
_Static_assert(
    sizeof(open_cfw_queue_delete_control) == 0x50U,
    "G2 FreeRTOS Queue_t ABI changed");
_Static_assert(
    __builtin_offsetof(
        open_cfw_queue_delete_control,
        ucStaticallyAllocated) == 0x46U,
    "G2 Queue_t static-allocation marker offset changed");
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_DELETE_ASSERT
extern open_cfw_queue_delete_ubase_type ulSetInterruptMask(void);
#define OPEN_CFW_FREERTOS_QUEUE_DELETE_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)ulSetInterruptMask(); \
            *(volatile open_cfw_queue_delete_ubase_type *) \
                (__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
            for (;;) { \
                __asm__ volatile("" ::: "memory"); \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_DELETE_FREE
extern void open_cfw_freertos_heap4_free(void *allocation);
#define OPEN_CFW_FREERTOS_QUEUE_DELETE_FREE(allocation) \
    open_cfw_freertos_heap4_free((allocation))
#endif

#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configSUPPORT_STATIC_ALLOCATION 1
#define configQUEUE_REGISTRY_SIZE 0
#define configUSE_TRACE_FACILITY 1
#define pdFALSE 0
#define configASSERT(condition) \
    OPEN_CFW_FREERTOS_QUEUE_DELETE_ASSERT(condition)
#define traceQUEUE_DELETE(queue) ((void)(queue))
#define mtCOVERAGE_TEST_MARKER() ((void)0)
#define vPortFree(allocation) \
    OPEN_CFW_FREERTOS_QUEUE_DELETE_FREE(allocation)
#define vQueueDelete open_cfw_freertos_queue_delete

__attribute__((used, noinline))
void vQueueDelete( QueueHandle_t xQueue )
{
    Queue_t * const pxQueue = xQueue;

    configASSERT( pxQueue );
    traceQUEUE_DELETE( pxQueue );

    #if ( configQUEUE_REGISTRY_SIZE > 0 )
    {
        vQueueUnregisterQueue( pxQueue );
    }
    #endif

    #if ( ( configSUPPORT_DYNAMIC_ALLOCATION == 1 ) && ( configSUPPORT_STATIC_ALLOCATION == 0 ) )
    {
        /* The queue can only have been allocated dynamically - free it
         * again. */
        vPortFree( pxQueue );
    }
    #elif ( ( configSUPPORT_DYNAMIC_ALLOCATION == 1 ) && ( configSUPPORT_STATIC_ALLOCATION == 1 ) )
    {
        /* The queue could have been allocated statically or dynamically, so
         * check before attempting to free the memory. */
        if( pxQueue->ucStaticallyAllocated == ( uint8_t ) pdFALSE )
        {
            vPortFree( pxQueue );
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }
    }
    #else /* if ( ( configSUPPORT_DYNAMIC_ALLOCATION == 1 ) && ( configSUPPORT_STATIC_ALLOCATION == 0 ) ) */
    {
        /* The queue must have been statically allocated, so is not going to be
         * deleted.  Avoid compiler warnings about the unused parameter. */
        ( void ) pxQueue;
    }
    #endif /* configSUPPORT_DYNAMIC_ALLOCATION */
}

#undef vQueueDelete
#undef vPortFree
#undef mtCOVERAGE_TEST_MARKER
#undef traceQUEUE_DELETE
#undef configASSERT
#undef pdFALSE
#undef configUSE_TRACE_FACILITY
#undef configQUEUE_REGISTRY_SIZE
#undef configSUPPORT_STATIC_ALLOCATION
#undef configSUPPORT_DYNAMIC_ALLOCATION
