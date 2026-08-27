/*
 * Copyright (c) 2006-2016, Matthew Conte
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded freestanding adaptation of the TLSF v3.1 control, pool, allocation,
 * and release entries present in the authenticated G2 bootloader ILP32 ABI.
 */

typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_public_word;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_tlsf_public_uintptr;
typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_public_size;

enum {
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FL_INDEX_COUNT = 24U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_SL_INDEX_COUNT = 32U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALIGNMENT = 4U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_HEADER_OVERHEAD = 4U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MIN = 12U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MAX = 0x40000000U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CONTROL_SIZE = 0x0C74U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FILE_ADDRESS = 0x00431A04U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALREADY_FREE_ADDRESS = 0x00431E00U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ADD_POOL_ALIGNMENT_FORMAT = 0x004320E0U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ADD_POOL_SIZE_FORMAT = 0x0043190CU,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CREATE_ALIGNMENT_FORMAT = 0x00432114U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ASSERT_THUMB_ADDRESS = 0x00415735U,
    OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_LOG_THUMB_ADDRESS = 0x00415FAFU
};

typedef struct open_cfw_bootloader_tlsf_public_block
    open_cfw_bootloader_tlsf_public_block;

struct open_cfw_bootloader_tlsf_public_block {
    open_cfw_bootloader_tlsf_public_block *previous_physical_block;
    open_cfw_bootloader_tlsf_public_word size;
    open_cfw_bootloader_tlsf_public_block *next_free;
    open_cfw_bootloader_tlsf_public_block *previous_free;
};

typedef struct open_cfw_bootloader_tlsf_public_control {
    open_cfw_bootloader_tlsf_public_block block_null;
    open_cfw_bootloader_tlsf_public_word first_level_bitmap;
    open_cfw_bootloader_tlsf_public_word second_level_bitmap[
        OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FL_INDEX_COUNT];
    open_cfw_bootloader_tlsf_public_block *blocks[
        OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FL_INDEX_COUNT]
        [OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_SL_INDEX_COUNT];
} open_cfw_bootloader_tlsf_public_control;

#if !defined(OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_HOST)
_Static_assert(sizeof(open_cfw_bootloader_tlsf_public_block) == 16U,
    "authenticated G2 TLSF block header must remain 16 bytes");
_Static_assert(sizeof(open_cfw_bootloader_tlsf_public_control) ==
        OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CONTROL_SIZE,
    "authenticated G2 TLSF control size changed");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_public_control, first_level_bitmap) == 16U,
    "authenticated G2 TLSF first-level bitmap offset changed");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_public_control, second_level_bitmap) == 20U,
    "authenticated G2 TLSF second-level bitmap offset changed");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_public_control, blocks) == 116U,
    "authenticated G2 TLSF free-list matrix offset changed");
#endif

typedef void (*open_cfw_bootloader_tlsf_public_assert_fn)(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_public_word line);
typedef void (*open_cfw_bootloader_tlsf_public_log2_fn)(
    const char *format,
    open_cfw_bootloader_tlsf_public_word first);
typedef void (*open_cfw_bootloader_tlsf_public_log3_fn)(
    const char *format,
    open_cfw_bootloader_tlsf_public_word first,
    open_cfw_bootloader_tlsf_public_word second);

open_cfw_bootloader_tlsf_public_size
open_cfw_bootloader_tlsf_align_down_416b7a(
    open_cfw_bootloader_tlsf_public_size value,
    open_cfw_bootloader_tlsf_public_size alignment);
open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_offset_to_block_416aa6(
    const void *pointer,
    open_cfw_bootloader_tlsf_public_size offset);
void open_cfw_bootloader_tlsf_block_set_size_416a10(
    open_cfw_bootloader_tlsf_public_block *block,
    open_cfw_bootloader_tlsf_public_word size);
void open_cfw_bootloader_tlsf_block_set_free_416a4c(
    open_cfw_bootloader_tlsf_public_block *block);
void open_cfw_bootloader_tlsf_block_set_used_416a5a(
    open_cfw_bootloader_tlsf_public_block *block);
void open_cfw_bootloader_tlsf_block_set_previous_free_416a74(
    open_cfw_bootloader_tlsf_public_block *block);
void open_cfw_bootloader_tlsf_block_set_previous_used_416a82(
    open_cfw_bootloader_tlsf_public_block *block);
open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_from_pointer_416a90(const void *pointer);
open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_link_next_416b14(
    open_cfw_bootloader_tlsf_public_block *block);
open_cfw_bootloader_tlsf_public_size
open_cfw_bootloader_tlsf_adjust_request_size_416bce(
    open_cfw_bootloader_tlsf_public_size size,
    open_cfw_bootloader_tlsf_public_size alignment);
int open_cfw_bootloader_tlsf_block_is_free_416a40(
    const open_cfw_bootloader_tlsf_public_block *block);
void open_cfw_bootloader_tlsf_block_insert_416e26(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block);
open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_locate_free_41707c(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_size size);
void *open_cfw_bootloader_tlsf_block_prepare_used_4170de(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block,
    open_cfw_bootloader_tlsf_public_size size);
void open_cfw_bootloader_tlsf_block_mark_as_free_416b22(
    open_cfw_bootloader_tlsf_public_block *block);
open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_merge_previous_416f62(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block);
open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_merge_next_416fc6(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block);

#if defined(OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_HOST)
void open_cfw_bootloader_tlsf_public_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_public_word line);
void open_cfw_bootloader_tlsf_public_host_log(
    const char *format,
    open_cfw_bootloader_tlsf_public_word first,
    open_cfw_bootloader_tlsf_public_word second);
#endif

static __attribute__((always_inline)) inline void
open_cfw_bootloader_tlsf_public_require(
    int condition,
    open_cfw_bootloader_tlsf_public_word expression_address,
    open_cfw_bootloader_tlsf_public_word line)
{
    if (!condition) {
#if defined(OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_HOST)
        open_cfw_bootloader_tlsf_public_host_assert(
            (const char *)(open_cfw_bootloader_tlsf_public_uintptr)
                expression_address,
            (const char *)(open_cfw_bootloader_tlsf_public_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FILE_ADDRESS,
            line);
#else
        ((open_cfw_bootloader_tlsf_public_assert_fn)
            (open_cfw_bootloader_tlsf_public_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ASSERT_THUMB_ADDRESS)(
                    (const char *)(open_cfw_bootloader_tlsf_public_uintptr)
                        expression_address,
                    (const char *)(open_cfw_bootloader_tlsf_public_uintptr)
                        OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FILE_ADDRESS,
                    line);
#endif
    }
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_tlsf_public_log2(
    open_cfw_bootloader_tlsf_public_word format_address,
    open_cfw_bootloader_tlsf_public_word first)
{
#if defined(OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_HOST)
    open_cfw_bootloader_tlsf_public_host_log(
        (const char *)(open_cfw_bootloader_tlsf_public_uintptr)format_address,
        first,
        0U);
#else
    ((open_cfw_bootloader_tlsf_public_log2_fn)
        (open_cfw_bootloader_tlsf_public_uintptr)
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_LOG_THUMB_ADDRESS)(
                (const char *)(open_cfw_bootloader_tlsf_public_uintptr)
                    format_address,
                first);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_tlsf_public_log3(
    open_cfw_bootloader_tlsf_public_word format_address,
    open_cfw_bootloader_tlsf_public_word first,
    open_cfw_bootloader_tlsf_public_word second)
{
#if defined(OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_HOST)
    open_cfw_bootloader_tlsf_public_host_log(
        (const char *)(open_cfw_bootloader_tlsf_public_uintptr)format_address,
        first,
        second);
#else
    ((open_cfw_bootloader_tlsf_public_log3_fn)
        (open_cfw_bootloader_tlsf_public_uintptr)
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_LOG_THUMB_ADDRESS)(
                (const char *)(open_cfw_bootloader_tlsf_public_uintptr)
                    format_address,
                first,
                second);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_control_construct_41711c(
    open_cfw_bootloader_tlsf_public_control *control)
{
    open_cfw_bootloader_tlsf_public_word first;
    open_cfw_bootloader_tlsf_public_word second;

    control->block_null.next_free = &control->block_null;
    control->block_null.previous_free = &control->block_null;
    control->first_level_bitmap = 0U;
    for (first = 0U;
         first < OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FL_INDEX_COUNT;
         ++first) {
        control->second_level_bitmap[first] = 0U;
        for (second = 0U;
             second < OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_SL_INDEX_COUNT;
             ++second) {
            control->blocks[first][second] = &control->block_null;
        }
    }
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_public_size
open_cfw_bootloader_tlsf_pool_overhead_41714c(void)
{
    return 2U * OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_HEADER_OVERHEAD;
}

__attribute__((used, noinline))
void *open_cfw_bootloader_tlsf_add_pool_41715c(
    open_cfw_bootloader_tlsf_public_control *control,
    void *memory,
    open_cfw_bootloader_tlsf_public_size bytes)
{
    open_cfw_bootloader_tlsf_public_block *block;
    open_cfw_bootloader_tlsf_public_block *next;
    const open_cfw_bootloader_tlsf_public_size overhead =
        open_cfw_bootloader_tlsf_pool_overhead_41714c();
    const open_cfw_bootloader_tlsf_public_size pool_bytes =
        open_cfw_bootloader_tlsf_align_down_416b7a(
            bytes - overhead,
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALIGNMENT);

    if (((open_cfw_bootloader_tlsf_public_uintptr)memory &
            (OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALIGNMENT - 1U)) != 0U) {
        open_cfw_bootloader_tlsf_public_log2(
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ADD_POOL_ALIGNMENT_FORMAT,
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALIGNMENT);
        return (void *)0;
    }

    if (pool_bytes < OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MIN ||
            pool_bytes > OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MAX) {
        open_cfw_bootloader_tlsf_public_log3(
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ADD_POOL_SIZE_FORMAT,
            overhead + OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MIN,
            overhead + OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MAX);
        return (void *)0;
    }

    block = open_cfw_bootloader_tlsf_offset_to_block_416aa6(
        memory,
        (open_cfw_bootloader_tlsf_public_size)(
            0U - OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_HEADER_OVERHEAD));
    open_cfw_bootloader_tlsf_block_set_size_416a10(block, pool_bytes);
    open_cfw_bootloader_tlsf_block_set_free_416a4c(block);
    open_cfw_bootloader_tlsf_block_set_previous_used_416a82(block);
    open_cfw_bootloader_tlsf_block_insert_416e26(control, block);

    next = open_cfw_bootloader_tlsf_block_link_next_416b14(block);
    open_cfw_bootloader_tlsf_block_set_size_416a10(next, 0U);
    open_cfw_bootloader_tlsf_block_set_used_416a5a(next);
    open_cfw_bootloader_tlsf_block_set_previous_free_416a74(next);
    return memory;
}

__attribute__((used, noinline))
void *open_cfw_bootloader_tlsf_create_417208(void *memory)
{
    if (((open_cfw_bootloader_tlsf_public_uintptr)memory &
            (OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALIGNMENT - 1U)) != 0U) {
        open_cfw_bootloader_tlsf_public_log2(
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CREATE_ALIGNMENT_FORMAT,
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALIGNMENT);
        return (void *)0;
    }
    open_cfw_bootloader_tlsf_control_construct_41711c(
        (open_cfw_bootloader_tlsf_public_control *)memory);
    return memory;
}

__attribute__((used, noinline))
void *open_cfw_bootloader_tlsf_create_with_pool_417240(
    void *memory,
    open_cfw_bootloader_tlsf_public_size bytes)
{
    void *const control = open_cfw_bootloader_tlsf_create_417208(memory);
    (void)open_cfw_bootloader_tlsf_add_pool_41715c(
        (open_cfw_bootloader_tlsf_public_control *)control,
        (void *)((unsigned char *)memory +
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CONTROL_SIZE),
        bytes - OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CONTROL_SIZE);
    return control;
}

__attribute__((used, noinline))
void *open_cfw_bootloader_tlsf_malloc_41726a(
    void *tlsf,
    open_cfw_bootloader_tlsf_public_size size)
{
    open_cfw_bootloader_tlsf_public_control *const control =
        (open_cfw_bootloader_tlsf_public_control *)tlsf;
    const open_cfw_bootloader_tlsf_public_size adjusted =
        open_cfw_bootloader_tlsf_adjust_request_size_416bce(
            size,
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALIGNMENT);
    open_cfw_bootloader_tlsf_public_block *const block =
        open_cfw_bootloader_tlsf_block_locate_free_41707c(
            control,
            adjusted);
    return open_cfw_bootloader_tlsf_block_prepare_used_4170de(
        control,
        block,
        adjusted);
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_free_417290(void *tlsf, void *pointer)
{
    if (pointer != (void *)0) {
        open_cfw_bootloader_tlsf_public_control *const control =
            (open_cfw_bootloader_tlsf_public_control *)tlsf;
        open_cfw_bootloader_tlsf_public_block *block =
            open_cfw_bootloader_tlsf_block_from_pointer_416a90(pointer);
        open_cfw_bootloader_tlsf_public_require(
            !open_cfw_bootloader_tlsf_block_is_free_416a40(block),
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALREADY_FREE_ADDRESS,
            1188U);
        open_cfw_bootloader_tlsf_block_mark_as_free_416b22(block);
        block = open_cfw_bootloader_tlsf_block_merge_previous_416f62(
            control,
            block);
        block = open_cfw_bootloader_tlsf_block_merge_next_416fc6(
            control,
            block);
        open_cfw_bootloader_tlsf_block_insert_416e26(control, block);
    }
}
