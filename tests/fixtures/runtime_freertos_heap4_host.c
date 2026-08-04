/*
 * SPDX-License-Identifier: MIT
 *
 * Host harness for the bounded G2 FreeRTOS V10.5.1 heap_4 closure.
 */

#include <setjmp.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum {
    OPEN_CFW_TEST_HEAP4_BYTES = 0x0002F000U,
    OPEN_CFW_TEST_HEAP4_NULL_OFFSET = 0xFFFFFFFFU
};

static _Alignas(16) unsigned char
open_cfw_test_heap4_heap[OPEN_CFW_TEST_HEAP4_BYTES];
static _Alignas(16) unsigned char open_cfw_test_heap4_start[32];
static _Alignas(16) unsigned char open_cfw_test_heap4_end_pointer[16];
static uint32_t open_cfw_test_heap4_free_bytes;
static uint32_t open_cfw_test_heap4_minimum_bytes;
static uint32_t open_cfw_test_heap4_allocation_count;
static uint32_t open_cfw_test_heap4_free_count;

static uint32_t open_cfw_test_heap4_suspend_count;
static uint32_t open_cfw_test_heap4_resume_count;
static uint32_t open_cfw_test_heap4_malloc_failed_count;
static uint32_t open_cfw_test_heap4_assert_count;
static jmp_buf open_cfw_test_heap4_assert_jump;
static int open_cfw_test_heap4_assert_jump_active;

static void open_cfw_test_heap4_suspend_all(void)
{
    open_cfw_test_heap4_suspend_count++;
}

static unsigned int open_cfw_test_heap4_resume_all(void)
{
    open_cfw_test_heap4_resume_count++;
    return 0U;
}

static void open_cfw_test_heap4_malloc_failed(void)
{
    open_cfw_test_heap4_malloc_failed_count++;
}

static void open_cfw_test_heap4_assert_fail(void)
    __attribute__((noreturn));

static void open_cfw_test_heap4_assert_fail(void)
{
    open_cfw_test_heap4_assert_count++;
    if (open_cfw_test_heap4_assert_jump_active != 0) {
        longjmp(open_cfw_test_heap4_assert_jump, 1);
    }
    abort();
}

#define OPEN_CFW_FREERTOS_HEAP4_HEAP_ADDRESS \
    ((__UINTPTR_TYPE__)(void *)open_cfw_test_heap4_heap)
#define OPEN_CFW_FREERTOS_HEAP4_START_ADDRESS \
    ((__UINTPTR_TYPE__)(void *)open_cfw_test_heap4_start)
#define OPEN_CFW_FREERTOS_HEAP4_END_POINTER_ADDRESS \
    ((__UINTPTR_TYPE__)(void *)open_cfw_test_heap4_end_pointer)
#define OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES_ADDRESS \
    ((__UINTPTR_TYPE__)(void *)&open_cfw_test_heap4_free_bytes)
#define OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES_ADDRESS \
    ((__UINTPTR_TYPE__)(void *)&open_cfw_test_heap4_minimum_bytes)
#define OPEN_CFW_FREERTOS_HEAP4_ALLOCATION_COUNT_ADDRESS \
    ((__UINTPTR_TYPE__)(void *)&open_cfw_test_heap4_allocation_count)
#define OPEN_CFW_FREERTOS_HEAP4_FREE_COUNT_ADDRESS \
    ((__UINTPTR_TYPE__)(void *)&open_cfw_test_heap4_free_count)
#define OPEN_CFW_FREERTOS_HEAP4_SUSPEND_ALL() \
    open_cfw_test_heap4_suspend_all()
#define OPEN_CFW_FREERTOS_HEAP4_RESUME_ALL() \
    ((void)open_cfw_test_heap4_resume_all())
#define OPEN_CFW_FREERTOS_HEAP4_MALLOC_FAILED() \
    open_cfw_test_heap4_malloc_failed()
#define OPEN_CFW_FREERTOS_HEAP4_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            open_cfw_test_heap4_assert_fail(); \
        } \
    } while (0)

#include \
    "../../components/apollo_main/core_overlay/runtime_freertos_heap4.c"

static uint32_t open_cfw_test_heap4_pointer_offset(const void *pointer)
{
    const unsigned char *bytes = (const unsigned char *)pointer;

    if (pointer == (const void *)0) {
        return OPEN_CFW_TEST_HEAP4_NULL_OFFSET;
    }
    if (
        bytes < open_cfw_test_heap4_heap ||
        bytes > open_cfw_test_heap4_heap + OPEN_CFW_TEST_HEAP4_BYTES
    ) {
        return OPEN_CFW_TEST_HEAP4_NULL_OFFSET;
    }
    return (uint32_t)(bytes - open_cfw_test_heap4_heap);
}

void open_cfw_test_freertos_heap4_reset(void)
{
    memset(
        open_cfw_test_heap4_heap,
        0xA5,
        sizeof(open_cfw_test_heap4_heap)
    );
    memset(
        open_cfw_test_heap4_start,
        0,
        sizeof(open_cfw_test_heap4_start)
    );
    memset(
        open_cfw_test_heap4_end_pointer,
        0,
        sizeof(open_cfw_test_heap4_end_pointer)
    );
    open_cfw_test_heap4_free_bytes = 0U;
    open_cfw_test_heap4_minimum_bytes = 0U;
    open_cfw_test_heap4_allocation_count = 0U;
    open_cfw_test_heap4_free_count = 0U;
    open_cfw_test_heap4_suspend_count = 0U;
    open_cfw_test_heap4_resume_count = 0U;
    open_cfw_test_heap4_malloc_failed_count = 0U;
    open_cfw_test_heap4_assert_count = 0U;
    open_cfw_test_heap4_assert_jump_active = 0;
}

void open_cfw_test_freertos_heap4_init(void)
{
    open_cfw_freertos_heap4_init();
}

uint32_t open_cfw_test_freertos_heap4_malloc(uint32_t wanted_size)
{
    return open_cfw_test_heap4_pointer_offset(
        open_cfw_freertos_heap4_malloc(wanted_size)
    );
}

uint32_t open_cfw_test_freertos_heap4_free(uint32_t payload_offset)
{
    void *memory;

    if (payload_offset == OPEN_CFW_TEST_HEAP4_NULL_OFFSET) {
        memory = (void *)0;
    } else {
        memory = (void *)(open_cfw_test_heap4_heap + payload_offset);
    }

    open_cfw_test_heap4_assert_jump_active = 1;
    if (setjmp(open_cfw_test_heap4_assert_jump) != 0) {
        open_cfw_test_heap4_assert_jump_active = 0;
        return 1U;
    }
    open_cfw_freertos_heap4_free(memory);
    open_cfw_test_heap4_assert_jump_active = 0;
    return 0U;
}

uint32_t open_cfw_test_freertos_heap4_get_struct_size(void)
{
    return OPEN_CFW_FREERTOS_HEAP4_STRUCT_SIZE;
}

uint32_t open_cfw_test_freertos_heap4_get_minimum_block_size(void)
{
    return OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BLOCK_SIZE;
}

uint32_t open_cfw_test_freertos_heap4_get_end_offset(void)
{
    return open_cfw_test_heap4_pointer_offset(
        OPEN_CFW_FREERTOS_HEAP4_END
    );
}

uint32_t open_cfw_test_freertos_heap4_get_start_next_offset(void)
{
    return open_cfw_test_heap4_pointer_offset(
        OPEN_CFW_FREERTOS_HEAP4_START.next_free_block
    );
}

uint32_t open_cfw_test_freertos_heap4_get_block_next_offset(
    uint32_t block_offset
)
{
    struct open_cfw_freertos_heap4_block *block =
        (void *)(open_cfw_test_heap4_heap + block_offset);

    return open_cfw_test_heap4_pointer_offset(block->next_free_block);
}

uint32_t open_cfw_test_freertos_heap4_get_block_size(
    uint32_t block_offset
)
{
    struct open_cfw_freertos_heap4_block *block =
        (void *)(open_cfw_test_heap4_heap + block_offset);

    return block->block_size;
}

uint32_t open_cfw_test_freertos_heap4_get_free_bytes(void)
{
    return open_cfw_test_heap4_free_bytes;
}

uint32_t open_cfw_test_freertos_heap4_get_minimum_bytes(void)
{
    return open_cfw_test_heap4_minimum_bytes;
}

uint32_t open_cfw_test_freertos_heap4_get_allocation_count(void)
{
    return open_cfw_test_heap4_allocation_count;
}

uint32_t open_cfw_test_freertos_heap4_get_free_count(void)
{
    return open_cfw_test_heap4_free_count;
}

uint32_t open_cfw_test_freertos_heap4_get_suspend_count(void)
{
    return open_cfw_test_heap4_suspend_count;
}

uint32_t open_cfw_test_freertos_heap4_get_resume_count(void)
{
    return open_cfw_test_heap4_resume_count;
}

uint32_t open_cfw_test_freertos_heap4_get_malloc_failed_count(void)
{
    return open_cfw_test_heap4_malloc_failed_count;
}

uint32_t open_cfw_test_freertos_heap4_get_assert_count(void)
{
    return open_cfw_test_heap4_assert_count;
}
