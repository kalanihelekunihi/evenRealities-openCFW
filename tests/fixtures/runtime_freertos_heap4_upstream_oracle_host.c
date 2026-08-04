/*
 * SPDX-License-Identifier: MIT
 *
 * Independent host oracle compiling the authenticated pristine
 * FreeRTOS-Kernel V10.5.1 portable/MemMang/heap_4.c.  Standard headers are
 * included before the size_t token is narrowed so the upstream algorithm runs
 * with the G2 32-bit size arithmetic while retaining native host pointers.
 */

#include <setjmp.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct open_cfw_oracle_heap_stats {
    uint32_t xAvailableHeapSpaceInBytes;
    uint32_t xSizeOfLargestFreeBlockInBytes;
    uint32_t xSizeOfSmallestFreeBlockInBytes;
    uint32_t xNumberOfFreeBlocks;
    uint32_t xMinimumEverFreeBytesRemaining;
    uint32_t xNumberOfSuccessfulAllocations;
    uint32_t xNumberOfSuccessfulFrees;
} HeapStats_t;

enum {
    OPEN_CFW_ORACLE_HEAP4_BYTES = 0x0002F000U,
    OPEN_CFW_ORACLE_HEAP4_NULL_OFFSET = 0xFFFFFFFFU
};

_Alignas(16) uint8_t ucHeap[OPEN_CFW_ORACLE_HEAP4_BYTES];

static uint32_t open_cfw_oracle_heap4_suspend_count;
static uint32_t open_cfw_oracle_heap4_resume_count;
static uint32_t open_cfw_oracle_heap4_malloc_failed_count;
static uint32_t open_cfw_oracle_heap4_assert_count;
static jmp_buf open_cfw_oracle_heap4_assert_jump;
static int open_cfw_oracle_heap4_assert_jump_active;

static void open_cfw_oracle_heap4_suspend_all(void)
{
    open_cfw_oracle_heap4_suspend_count++;
}

static unsigned int open_cfw_oracle_heap4_resume_all(void)
{
    open_cfw_oracle_heap4_resume_count++;
    return 0U;
}

static void open_cfw_oracle_heap4_malloc_failed(void)
{
    open_cfw_oracle_heap4_malloc_failed_count++;
}

static void open_cfw_oracle_heap4_assert_fail(void)
    __attribute__((noreturn));

static void open_cfw_oracle_heap4_assert_fail(void)
{
    open_cfw_oracle_heap4_assert_count++;
    if (open_cfw_oracle_heap4_assert_jump_active != 0) {
        longjmp(open_cfw_oracle_heap4_assert_jump, 1);
    }
    abort();
}

#define INC_FREERTOS_H
#define INC_TASK_H
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configAPPLICATION_ALLOCATED_HEAP 1
#define configTOTAL_HEAP_SIZE OPEN_CFW_ORACLE_HEAP4_BYTES
#define configHEAP_CLEAR_MEMORY_ON_FREE 0
#define configUSE_MALLOC_FAILED_HOOK 1
#define portBYTE_ALIGNMENT 8U
#define portBYTE_ALIGNMENT_MASK 7U
#define portPOINTER_SIZE_TYPE uintptr_t
#define portMAX_DELAY 0xFFFFFFFFU
#define PRIVILEGED_DATA
#define PRIVILEGED_FUNCTION
#define mtCOVERAGE_TEST_MARKER()
#define traceMALLOC(pointer, size)
#define traceFREE(pointer, size)
#define taskENTER_CRITICAL()
#define taskEXIT_CRITICAL()
#define vTaskSuspendAll open_cfw_oracle_heap4_suspend_all
#define xTaskResumeAll open_cfw_oracle_heap4_resume_all
#define vApplicationMallocFailedHook open_cfw_oracle_heap4_malloc_failed
#define configASSERT(condition) \
    do { \
        if (!(condition)) { \
            open_cfw_oracle_heap4_assert_fail(); \
        } \
    } while (0)

#define pvPortMalloc open_cfw_oracle_heap4_pvPortMalloc
#define vPortFree open_cfw_oracle_heap4_vPortFree
#define xPortGetFreeHeapSize open_cfw_oracle_heap4_xPortGetFreeHeapSize
#define xPortGetMinimumEverFreeHeapSize \
    open_cfw_oracle_heap4_xPortGetMinimumEverFreeHeapSize
#define vPortInitialiseBlocks \
    open_cfw_oracle_heap4_vPortInitialiseBlocks
#define pvPortCalloc open_cfw_oracle_heap4_pvPortCalloc
#define vPortGetHeapStats open_cfw_oracle_heap4_vPortGetHeapStats

#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wpointer-to-int-cast"
#pragma clang diagnostic ignored "-Wvoid-pointer-to-int-cast"
#endif
#define size_t uint32_t
#include "../../third_party/freertos-kernel/portable/MemMang/heap_4.c"
#undef size_t
#if defined(__clang__)
#pragma clang diagnostic pop
#endif

static uint32_t open_cfw_oracle_heap4_pointer_offset(
    const void *pointer
)
{
    const unsigned char *bytes = (const unsigned char *)pointer;

    if (pointer == (const void *)0) {
        return OPEN_CFW_ORACLE_HEAP4_NULL_OFFSET;
    }
    if (bytes < ucHeap || bytes > ucHeap + OPEN_CFW_ORACLE_HEAP4_BYTES) {
        return OPEN_CFW_ORACLE_HEAP4_NULL_OFFSET;
    }
    return (uint32_t)(bytes - ucHeap);
}

void open_cfw_oracle_freertos_heap4_reset(void)
{
    memset(ucHeap, 0xA5, sizeof(ucHeap));
    memset(&xStart, 0, sizeof(xStart));
    pxEnd = NULL;
    xFreeBytesRemaining = 0U;
    xMinimumEverFreeBytesRemaining = 0U;
    xNumberOfSuccessfulAllocations = 0U;
    xNumberOfSuccessfulFrees = 0U;
    open_cfw_oracle_heap4_suspend_count = 0U;
    open_cfw_oracle_heap4_resume_count = 0U;
    open_cfw_oracle_heap4_malloc_failed_count = 0U;
    open_cfw_oracle_heap4_assert_count = 0U;
    open_cfw_oracle_heap4_assert_jump_active = 0;
}

void open_cfw_oracle_freertos_heap4_init(void)
{
    prvHeapInit();
}

uint32_t open_cfw_oracle_freertos_heap4_malloc(uint32_t wanted_size)
{
    return open_cfw_oracle_heap4_pointer_offset(
        open_cfw_oracle_heap4_pvPortMalloc(wanted_size)
    );
}

uint32_t open_cfw_oracle_freertos_heap4_free(uint32_t payload_offset)
{
    void *memory;

    if (payload_offset == OPEN_CFW_ORACLE_HEAP4_NULL_OFFSET) {
        memory = (void *)0;
    } else {
        memory = (void *)(ucHeap + payload_offset);
    }

    open_cfw_oracle_heap4_assert_jump_active = 1;
    if (setjmp(open_cfw_oracle_heap4_assert_jump) != 0) {
        open_cfw_oracle_heap4_assert_jump_active = 0;
        return 1U;
    }
    open_cfw_oracle_heap4_vPortFree(memory);
    open_cfw_oracle_heap4_assert_jump_active = 0;
    return 0U;
}

uint32_t open_cfw_oracle_freertos_heap4_get_struct_size(void)
{
    return (uint32_t)xHeapStructSize;
}

uint32_t open_cfw_oracle_freertos_heap4_get_minimum_block_size(void)
{
    return (uint32_t)heapMINIMUM_BLOCK_SIZE;
}

uint32_t open_cfw_oracle_freertos_heap4_get_end_offset(void)
{
    return open_cfw_oracle_heap4_pointer_offset(pxEnd);
}

uint32_t open_cfw_oracle_freertos_heap4_get_start_next_offset(void)
{
    return open_cfw_oracle_heap4_pointer_offset(
        xStart.pxNextFreeBlock
    );
}

uint32_t open_cfw_oracle_freertos_heap4_get_block_next_offset(
    uint32_t block_offset
)
{
    BlockLink_t *block = (void *)(ucHeap + block_offset);

    return open_cfw_oracle_heap4_pointer_offset(block->pxNextFreeBlock);
}

uint32_t open_cfw_oracle_freertos_heap4_get_block_size(
    uint32_t block_offset
)
{
    BlockLink_t *block = (void *)(ucHeap + block_offset);

    return block->xBlockSize;
}

uint32_t open_cfw_oracle_freertos_heap4_get_free_bytes(void)
{
    return xFreeBytesRemaining;
}

uint32_t open_cfw_oracle_freertos_heap4_get_minimum_bytes(void)
{
    return xMinimumEverFreeBytesRemaining;
}

uint32_t open_cfw_oracle_freertos_heap4_get_allocation_count(void)
{
    return xNumberOfSuccessfulAllocations;
}

uint32_t open_cfw_oracle_freertos_heap4_get_free_count(void)
{
    return xNumberOfSuccessfulFrees;
}

uint32_t open_cfw_oracle_freertos_heap4_get_suspend_count(void)
{
    return open_cfw_oracle_heap4_suspend_count;
}

uint32_t open_cfw_oracle_freertos_heap4_get_resume_count(void)
{
    return open_cfw_oracle_heap4_resume_count;
}

uint32_t open_cfw_oracle_freertos_heap4_get_malloc_failed_count(void)
{
    return open_cfw_oracle_heap4_malloc_failed_count;
}

uint32_t open_cfw_oracle_freertos_heap4_get_assert_count(void)
{
    return open_cfw_oracle_heap4_assert_count;
}
