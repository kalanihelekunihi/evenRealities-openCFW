/*
 * Copyright (c) 2006-2016, Matthew Conte
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded freestanding adaptation of TLSF v3.1 free-list selection and
 * mutation helpers for the authenticated G2 bootloader ILP32 ABI.
 */

typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_list_word;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_tlsf_list_uintptr;

enum {
    OPEN_CFW_BOOTLOADER_TLSF_LIST_FL_INDEX_COUNT = 24U,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_SL_INDEX_COUNT = 32U,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_ALIGNMENT = 4U,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_FILE_ADDRESS = 0x00431A04U,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_SL_MAP_EXPRESSION_ADDRESS = 0x00431A40U,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_PREVIOUS_EXPRESSION_ADDRESS = 0x00432860U,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_CURRENT_EXPRESSION_ADDRESS = 0x00432598U,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_BLOCK_EXPRESSION_ADDRESS = 0x00431A7CU,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_NEXT_EXPRESSION_ADDRESS = 0x0043288CU,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_ALIGNED_EXPRESSION_ADDRESS = 0x00430D3CU,
    OPEN_CFW_BOOTLOADER_TLSF_LIST_ASSERT_THUMB_ADDRESS = 0x00415735U
};

typedef struct open_cfw_bootloader_tlsf_list_block
    open_cfw_bootloader_tlsf_list_block;

struct open_cfw_bootloader_tlsf_list_block {
    open_cfw_bootloader_tlsf_list_block *previous_physical_block;
    open_cfw_bootloader_tlsf_list_word size;
    open_cfw_bootloader_tlsf_list_block *next_free;
    open_cfw_bootloader_tlsf_list_block *previous_free;
};

typedef struct open_cfw_bootloader_tlsf_list_control {
    open_cfw_bootloader_tlsf_list_block block_null;
    open_cfw_bootloader_tlsf_list_word first_level_bitmap;
    open_cfw_bootloader_tlsf_list_word second_level_bitmap[
        OPEN_CFW_BOOTLOADER_TLSF_LIST_FL_INDEX_COUNT];
    open_cfw_bootloader_tlsf_list_block *blocks[
        OPEN_CFW_BOOTLOADER_TLSF_LIST_FL_INDEX_COUNT]
        [OPEN_CFW_BOOTLOADER_TLSF_LIST_SL_INDEX_COUNT];
} open_cfw_bootloader_tlsf_list_control;

#if !defined(OPEN_CFW_BOOTLOADER_TLSF_FREE_LISTS_HOST)
_Static_assert(sizeof(open_cfw_bootloader_tlsf_list_block) == 16U,
    "authenticated G2 TLSF block header must remain 16 bytes");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_list_control, first_level_bitmap) == 16U,
    "authenticated G2 TLSF first-level bitmap offset changed");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_list_control, second_level_bitmap) == 20U,
    "authenticated G2 TLSF second-level bitmap offset changed");
_Static_assert(__builtin_offsetof(
    open_cfw_bootloader_tlsf_list_control, blocks) == 116U,
    "authenticated G2 TLSF free-list matrix offset changed");
#endif

typedef void (*open_cfw_bootloader_tlsf_list_assert_fn)(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_list_word line);

open_cfw_bootloader_tlsf_list_word open_cfw_bootloader_runtime_ctz_4169e2(
    open_cfw_bootloader_tlsf_list_word value);
void *open_cfw_bootloader_tlsf_block_to_pointer_416a9c(
    const open_cfw_bootloader_tlsf_list_block *block);
void *open_cfw_bootloader_tlsf_align_pointer_416ba4(
    const void *pointer,
    __SIZE_TYPE__ alignment);

#if defined(OPEN_CFW_BOOTLOADER_TLSF_FREE_LISTS_HOST)
void open_cfw_bootloader_tlsf_free_lists_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_list_word line);
#endif

static __attribute__((always_inline)) inline void
open_cfw_bootloader_tlsf_list_require(
    int condition,
    open_cfw_bootloader_tlsf_list_word expression_address,
    open_cfw_bootloader_tlsf_list_word line)
{
    if (!condition) {
#if defined(OPEN_CFW_BOOTLOADER_TLSF_FREE_LISTS_HOST)
        open_cfw_bootloader_tlsf_free_lists_host_assert(
            (const char *)(open_cfw_bootloader_tlsf_list_uintptr)
                expression_address,
            (const char *)(open_cfw_bootloader_tlsf_list_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_LIST_FILE_ADDRESS,
            line);
#else
        ((open_cfw_bootloader_tlsf_list_assert_fn)
            (open_cfw_bootloader_tlsf_list_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_LIST_ASSERT_THUMB_ADDRESS)(
                    (const char *)(open_cfw_bootloader_tlsf_list_uintptr)
                        expression_address,
                    (const char *)(open_cfw_bootloader_tlsf_list_uintptr)
                        OPEN_CFW_BOOTLOADER_TLSF_LIST_FILE_ADDRESS,
                    line);
#endif
    }
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_list_block *
open_cfw_bootloader_tlsf_search_suitable_block_416c4e(
    open_cfw_bootloader_tlsf_list_control *control,
    int *first_level,
    int *second_level)
{
    int first = *first_level;
    int second = *second_level;
    open_cfw_bootloader_tlsf_list_word second_map =
        control->second_level_bitmap[first] & (~0U << second);

    if (second_map == 0U) {
        const open_cfw_bootloader_tlsf_list_word first_map =
            control->first_level_bitmap & (~0U << (first + 1));
        if (first_map == 0U) {
            return (open_cfw_bootloader_tlsf_list_block *)0;
        }

        first = (int)open_cfw_bootloader_runtime_ctz_4169e2(first_map);
        *first_level = first;
        second_map = control->second_level_bitmap[first];
    }

    open_cfw_bootloader_tlsf_list_require(
        second_map != 0U,
        OPEN_CFW_BOOTLOADER_TLSF_LIST_SL_MAP_EXPRESSION_ADDRESS,
        568U);
    second = (int)open_cfw_bootloader_runtime_ctz_4169e2(second_map);
    *second_level = second;
    return control->blocks[first][second];
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_remove_free_block_416cc6(
    open_cfw_bootloader_tlsf_list_control *control,
    open_cfw_bootloader_tlsf_list_block *block,
    int first,
    int second)
{
    open_cfw_bootloader_tlsf_list_block *previous = block->previous_free;
    open_cfw_bootloader_tlsf_list_block *next = block->next_free;

    open_cfw_bootloader_tlsf_list_require(
        previous != (open_cfw_bootloader_tlsf_list_block *)0,
        OPEN_CFW_BOOTLOADER_TLSF_LIST_PREVIOUS_EXPRESSION_ADDRESS,
        581U);
    open_cfw_bootloader_tlsf_list_require(
        next != (open_cfw_bootloader_tlsf_list_block *)0,
        OPEN_CFW_BOOTLOADER_TLSF_LIST_NEXT_EXPRESSION_ADDRESS,
        582U);
    next->previous_free = previous;
    previous->next_free = next;

    if (control->blocks[first][second] == block) {
        control->blocks[first][second] = next;
        if (next == &control->block_null) {
            control->second_level_bitmap[first] &= ~(1U << second);
            if (control->second_level_bitmap[first] == 0U) {
                control->first_level_bitmap &= ~(1U << first);
            }
        }
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_insert_free_block_416d5c(
    open_cfw_bootloader_tlsf_list_control *control,
    open_cfw_bootloader_tlsf_list_block *block,
    int first,
    int second)
{
    open_cfw_bootloader_tlsf_list_block *current =
        control->blocks[first][second];

    open_cfw_bootloader_tlsf_list_require(
        current != (open_cfw_bootloader_tlsf_list_block *)0,
        OPEN_CFW_BOOTLOADER_TLSF_LIST_CURRENT_EXPRESSION_ADDRESS,
        609U);
    open_cfw_bootloader_tlsf_list_require(
        block != (open_cfw_bootloader_tlsf_list_block *)0,
        OPEN_CFW_BOOTLOADER_TLSF_LIST_BLOCK_EXPRESSION_ADDRESS,
        610U);
    block->next_free = current;
    block->previous_free = &control->block_null;
    current->previous_free = block;

    open_cfw_bootloader_tlsf_list_require(
        open_cfw_bootloader_tlsf_block_to_pointer_416a9c(block) ==
            open_cfw_bootloader_tlsf_align_pointer_416ba4(
                open_cfw_bootloader_tlsf_block_to_pointer_416a9c(block),
                OPEN_CFW_BOOTLOADER_TLSF_LIST_ALIGNMENT),
        OPEN_CFW_BOOTLOADER_TLSF_LIST_ALIGNED_EXPRESSION_ADDRESS,
        616U);

    control->blocks[first][second] = block;
    control->first_level_bitmap |= 1U << first;
    control->second_level_bitmap[first] |= 1U << second;
}
