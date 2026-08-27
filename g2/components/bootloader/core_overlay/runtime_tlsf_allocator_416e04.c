/*
 * Copyright (c) 2006-2016, Matthew Conte
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded freestanding adaptation of TLSF v3.1 block allocation helpers for
 * the authenticated G2 bootloader ILP32 ABI.
 */

typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_allocator_word;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_tlsf_allocator_uintptr;
typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_allocator_size;

enum {
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_FL_INDEX_COUNT = 24U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_SL_INDEX_COUNT = 32U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HEADER_OVERHEAD = 4U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_HEADER_SIZE = 16U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_SIZE_MIN = 12U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_ALIGNMENT = 4U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_FILE_ADDRESS = 0x00431A04U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_REMAINING_ALIGNED_ADDRESS =
        0x00430CC8U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_SPLIT_SIZE_ADDRESS = 0x004318CCU,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_MINIMUM_SIZE_ADDRESS = 0x0043138CU,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_PREVIOUS_NOT_LAST_ADDRESS =
        0x00431D90U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_PREVIOUS_BLOCK_ADDRESS =
        0x004328B8U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_PREVIOUS_FREE_ADDRESS = 0x004314F8U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_NEXT_BLOCK_ADDRESS = 0x004328E4U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_NOT_LAST_ADDRESS = 0x00431DC8U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_FREE_ADDRESS = 0x004325C8U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_LOCATED_SIZE_ADDRESS = 0x00433738U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_NONZERO_SIZE_ADDRESS = 0x004320E0U,
    OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_ASSERT_THUMB_ADDRESS = 0x00415735U
};

typedef struct open_cfw_bootloader_tlsf_allocator_block
    open_cfw_bootloader_tlsf_allocator_block;

struct open_cfw_bootloader_tlsf_allocator_block {
    open_cfw_bootloader_tlsf_allocator_block *previous_physical_block;
    open_cfw_bootloader_tlsf_allocator_word size;
    open_cfw_bootloader_tlsf_allocator_block *next_free;
    open_cfw_bootloader_tlsf_allocator_block *previous_free;
};

typedef struct open_cfw_bootloader_tlsf_allocator_control {
    open_cfw_bootloader_tlsf_allocator_block block_null;
    open_cfw_bootloader_tlsf_allocator_word first_level_bitmap;
    open_cfw_bootloader_tlsf_allocator_word second_level_bitmap[
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_FL_INDEX_COUNT];
    open_cfw_bootloader_tlsf_allocator_block *blocks[
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_FL_INDEX_COUNT]
        [OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_SL_INDEX_COUNT];
} open_cfw_bootloader_tlsf_allocator_control;

#if !defined(OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HOST)
_Static_assert(sizeof(open_cfw_bootloader_tlsf_allocator_block) == 16U,
    "authenticated G2 TLSF block header must remain 16 bytes");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_allocator_control, first_level_bitmap) == 16U,
    "authenticated G2 TLSF first-level bitmap offset changed");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_allocator_control, second_level_bitmap) == 20U,
    "authenticated G2 TLSF second-level bitmap offset changed");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_allocator_control, blocks) == 116U,
    "authenticated G2 TLSF free-list matrix offset changed");
#endif

typedef void (*open_cfw_bootloader_tlsf_allocator_assert_fn)(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_allocator_word line);

open_cfw_bootloader_tlsf_allocator_word
open_cfw_bootloader_tlsf_block_size_4169fc(
    const open_cfw_bootloader_tlsf_allocator_block *block);
void open_cfw_bootloader_tlsf_block_set_size_416a10(
    open_cfw_bootloader_tlsf_allocator_block *block,
    open_cfw_bootloader_tlsf_allocator_word size);
int open_cfw_bootloader_tlsf_block_is_free_416a40(
    const open_cfw_bootloader_tlsf_allocator_block *block);
int open_cfw_bootloader_tlsf_block_is_last_416a2c(
    const open_cfw_bootloader_tlsf_allocator_block *block);
int open_cfw_bootloader_tlsf_block_is_previous_free_416a68(
    const open_cfw_bootloader_tlsf_allocator_block *block);
void open_cfw_bootloader_tlsf_block_set_previous_free_416a74(
    open_cfw_bootloader_tlsf_allocator_block *block);
void open_cfw_bootloader_tlsf_block_mark_as_free_416b22(
    open_cfw_bootloader_tlsf_allocator_block *block);
void open_cfw_bootloader_tlsf_block_mark_as_used_416b38(
    open_cfw_bootloader_tlsf_allocator_block *block);
void *open_cfw_bootloader_tlsf_block_to_pointer_416a9c(
    const open_cfw_bootloader_tlsf_allocator_block *block);
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_offset_to_block_416aa6(
    const void *pointer,
    open_cfw_bootloader_tlsf_allocator_size offset);
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_prev_416aaa(
    const open_cfw_bootloader_tlsf_allocator_block *block);
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_next_416ad0(
    const open_cfw_bootloader_tlsf_allocator_block *block);
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_link_next_416b14(
    open_cfw_bootloader_tlsf_allocator_block *block);
void *open_cfw_bootloader_tlsf_align_pointer_416ba4(
    const void *pointer,
    open_cfw_bootloader_tlsf_allocator_size alignment);
void open_cfw_bootloader_tlsf_mapping_insert_416bf8(
    open_cfw_bootloader_tlsf_allocator_size size,
    int *first_level,
    int *second_level);
void open_cfw_bootloader_tlsf_mapping_search_416c26(
    open_cfw_bootloader_tlsf_allocator_size size,
    int *first_level,
    int *second_level);
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_search_suitable_block_416c4e(
    open_cfw_bootloader_tlsf_allocator_control *control,
    int *first_level,
    int *second_level);
void open_cfw_bootloader_tlsf_remove_free_block_416cc6(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block,
    int first,
    int second);
void open_cfw_bootloader_tlsf_insert_free_block_416d5c(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block,
    int first,
    int second);

#if defined(OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HOST)
void open_cfw_bootloader_tlsf_allocator_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_allocator_word line);
#endif

static __attribute__((always_inline)) inline void
open_cfw_bootloader_tlsf_allocator_require(
    int condition,
    open_cfw_bootloader_tlsf_allocator_word expression_address,
    open_cfw_bootloader_tlsf_allocator_word line)
{
    if (!condition) {
#if defined(OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HOST)
        open_cfw_bootloader_tlsf_allocator_host_assert(
            (const char *)(open_cfw_bootloader_tlsf_allocator_uintptr)
                expression_address,
            (const char *)(open_cfw_bootloader_tlsf_allocator_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_FILE_ADDRESS,
            line);
#else
        ((open_cfw_bootloader_tlsf_allocator_assert_fn)
            (open_cfw_bootloader_tlsf_allocator_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_ASSERT_THUMB_ADDRESS)(
                    (const char *)(open_cfw_bootloader_tlsf_allocator_uintptr)
                        expression_address,
                    (const char *)(open_cfw_bootloader_tlsf_allocator_uintptr)
                        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_FILE_ADDRESS,
                    line);
#endif
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_remove_416e04(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    int first;
    int second;
    open_cfw_bootloader_tlsf_mapping_insert_416bf8(
        open_cfw_bootloader_tlsf_block_size_4169fc(block),
        &first,
        &second);
    open_cfw_bootloader_tlsf_remove_free_block_416cc6(
        control,
        block,
        first,
        second);
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_insert_416e26(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    int first;
    int second;
    open_cfw_bootloader_tlsf_mapping_insert_416bf8(
        open_cfw_bootloader_tlsf_block_size_4169fc(block),
        &first,
        &second);
    open_cfw_bootloader_tlsf_insert_free_block_416d5c(
        control,
        block,
        first,
        second);
}

__attribute__((used, noinline))
int open_cfw_bootloader_tlsf_block_can_split_416e48(
    open_cfw_bootloader_tlsf_allocator_block *block,
    open_cfw_bootloader_tlsf_allocator_size size)
{
    return open_cfw_bootloader_tlsf_block_size_4169fc(block) >=
        (open_cfw_bootloader_tlsf_allocator_size)(
            OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_HEADER_SIZE + size);
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_split_416e60(
    open_cfw_bootloader_tlsf_allocator_block *block,
    open_cfw_bootloader_tlsf_allocator_size size)
{
    void *const block_pointer =
        open_cfw_bootloader_tlsf_block_to_pointer_416a9c(block);
    open_cfw_bootloader_tlsf_allocator_block *remaining =
        open_cfw_bootloader_tlsf_offset_to_block_416aa6(
            block_pointer,
            size - OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HEADER_OVERHEAD);
    const open_cfw_bootloader_tlsf_allocator_size remaining_size =
        open_cfw_bootloader_tlsf_block_size_4169fc(block) -
        (size + OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HEADER_OVERHEAD);
    void *const remaining_pointer =
        open_cfw_bootloader_tlsf_block_to_pointer_416a9c(remaining);

    open_cfw_bootloader_tlsf_allocator_require(
        remaining_pointer ==
            open_cfw_bootloader_tlsf_align_pointer_416ba4(
                remaining_pointer,
                OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_ALIGNMENT),
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_REMAINING_ALIGNED_ADDRESS,
        657U);
    open_cfw_bootloader_tlsf_allocator_require(
        open_cfw_bootloader_tlsf_block_size_4169fc(block) ==
            remaining_size + size +
                OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HEADER_OVERHEAD,
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_SPLIT_SIZE_ADDRESS,
        659U);
    open_cfw_bootloader_tlsf_block_set_size_416a10(
        remaining,
        remaining_size);
    open_cfw_bootloader_tlsf_allocator_require(
        open_cfw_bootloader_tlsf_block_size_4169fc(remaining) >=
            OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_SIZE_MIN,
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_MINIMUM_SIZE_ADDRESS,
        661U);
    open_cfw_bootloader_tlsf_block_set_size_416a10(block, size);
    open_cfw_bootloader_tlsf_block_mark_as_free_416b22(remaining);
    return remaining;
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_absorb_416f20(
    open_cfw_bootloader_tlsf_allocator_block *previous,
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    open_cfw_bootloader_tlsf_allocator_require(
        !open_cfw_bootloader_tlsf_block_is_last_416a2c(previous),
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_PREVIOUS_NOT_LAST_ADDRESS,
        672U);
    previous->size += open_cfw_bootloader_tlsf_block_size_4169fc(block) +
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HEADER_OVERHEAD;
    (void)open_cfw_bootloader_tlsf_block_link_next_416b14(previous);
    return previous;
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_merge_previous_416f62(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    if (open_cfw_bootloader_tlsf_block_is_previous_free_416a68(block)) {
        open_cfw_bootloader_tlsf_allocator_block *previous =
            open_cfw_bootloader_tlsf_block_prev_416aaa(block);
        open_cfw_bootloader_tlsf_allocator_require(
            previous != (open_cfw_bootloader_tlsf_allocator_block *)0,
            OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_PREVIOUS_BLOCK_ADDRESS,
            685U);
        open_cfw_bootloader_tlsf_allocator_require(
            open_cfw_bootloader_tlsf_block_is_free_416a40(previous),
            OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_PREVIOUS_FREE_ADDRESS,
            686U);
        open_cfw_bootloader_tlsf_block_remove_416e04(control, previous);
        block = open_cfw_bootloader_tlsf_block_absorb_416f20(
            previous,
            block);
    }
    return block;
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_merge_next_416fc6(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    open_cfw_bootloader_tlsf_allocator_block *next =
        open_cfw_bootloader_tlsf_block_next_416ad0(block);
    open_cfw_bootloader_tlsf_allocator_require(
        next != (open_cfw_bootloader_tlsf_allocator_block *)0,
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_NEXT_BLOCK_ADDRESS,
        698U);
    if (open_cfw_bootloader_tlsf_block_is_free_416a40(next)) {
        open_cfw_bootloader_tlsf_allocator_require(
            !open_cfw_bootloader_tlsf_block_is_last_416a2c(block),
            OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_NOT_LAST_ADDRESS,
            702U);
        open_cfw_bootloader_tlsf_block_remove_416e04(control, next);
        block = open_cfw_bootloader_tlsf_block_absorb_416f20(block, next);
    }
    return block;
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_trim_free_41702a(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block,
    open_cfw_bootloader_tlsf_allocator_size size)
{
    open_cfw_bootloader_tlsf_allocator_require(
        open_cfw_bootloader_tlsf_block_is_free_416a40(block),
        OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_BLOCK_FREE_ADDRESS,
        713U);
    if (open_cfw_bootloader_tlsf_block_can_split_416e48(block, size)) {
        open_cfw_bootloader_tlsf_allocator_block *remaining =
            open_cfw_bootloader_tlsf_block_split_416e60(block, size);
        (void)open_cfw_bootloader_tlsf_block_link_next_416b14(block);
        open_cfw_bootloader_tlsf_block_set_previous_free_416a74(remaining);
        open_cfw_bootloader_tlsf_block_insert_416e26(control, remaining);
    }
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_locate_free_41707c(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_size size)
{
    int first = 0;
    int second = 0;
    open_cfw_bootloader_tlsf_allocator_block *block =
        (open_cfw_bootloader_tlsf_allocator_block *)0;

    if (size != 0U) {
        open_cfw_bootloader_tlsf_mapping_search_416c26(
            size,
            &first,
            &second);
        if (first < (int)OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_FL_INDEX_COUNT) {
            block = open_cfw_bootloader_tlsf_search_suitable_block_416c4e(
                control,
                &first,
                &second);
        }
    }

    if (block != (open_cfw_bootloader_tlsf_allocator_block *)0) {
        open_cfw_bootloader_tlsf_allocator_require(
            open_cfw_bootloader_tlsf_block_size_4169fc(block) >= size,
            OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_LOCATED_SIZE_ADDRESS,
            777U);
        open_cfw_bootloader_tlsf_remove_free_block_416cc6(
            control,
            block,
            first,
            second);
    }
    return block;
}

__attribute__((used, noinline))
void *open_cfw_bootloader_tlsf_block_prepare_used_4170de(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block,
    open_cfw_bootloader_tlsf_allocator_size size)
{
    void *pointer = (void *)0;
    if (block != (open_cfw_bootloader_tlsf_allocator_block *)0) {
        open_cfw_bootloader_tlsf_allocator_require(
            size != 0U,
            OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_NONZERO_SIZE_ADDRESS,
            789U);
        open_cfw_bootloader_tlsf_block_trim_free_41702a(
            control,
            block,
            size);
        open_cfw_bootloader_tlsf_block_mark_as_used_416b38(block);
        pointer = open_cfw_bootloader_tlsf_block_to_pointer_416a9c(block);
    }
    return pointer;
}
