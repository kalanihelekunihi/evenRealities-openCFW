#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define OPEN_CFW_BOOTLOADER_TLSF_ALLOCATOR_HOST 1
#include "../../components/bootloader/core_overlay/runtime_tlsf_allocator_416e04.c"

static unsigned int open_cfw_test_assert_count;
static uintptr_t open_cfw_test_assert_expression;
static unsigned int open_cfw_test_assert_line;
static open_cfw_bootloader_tlsf_allocator_block *open_cfw_test_primary;
static open_cfw_bootloader_tlsf_allocator_block *open_cfw_test_remaining;
static open_cfw_bootloader_tlsf_allocator_block *open_cfw_test_trailing;

void open_cfw_bootloader_tlsf_allocator_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_allocator_word line)
{
    (void)file;
    ++open_cfw_test_assert_count;
    open_cfw_test_assert_expression = (uintptr_t)expression;
    open_cfw_test_assert_line = line;
}

open_cfw_bootloader_tlsf_allocator_word
open_cfw_bootloader_tlsf_block_size_4169fc(
    const open_cfw_bootloader_tlsf_allocator_block *block)
{
    return block->size & ~3U;
}

void open_cfw_bootloader_tlsf_block_set_size_416a10(
    open_cfw_bootloader_tlsf_allocator_block *block,
    open_cfw_bootloader_tlsf_allocator_word size)
{
    block->size = size | (block->size & 3U);
}

int open_cfw_bootloader_tlsf_block_is_free_416a40(
    const open_cfw_bootloader_tlsf_allocator_block *block)
{
    return (int)(block->size & 1U);
}

int open_cfw_bootloader_tlsf_block_is_last_416a2c(
    const open_cfw_bootloader_tlsf_allocator_block *block)
{
    return open_cfw_bootloader_tlsf_block_size_4169fc(block) == 0U;
}

int open_cfw_bootloader_tlsf_block_is_previous_free_416a68(
    const open_cfw_bootloader_tlsf_allocator_block *block)
{
    return (int)(block->size & 2U);
}

void open_cfw_bootloader_tlsf_block_set_previous_free_416a74(
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    block->size |= 2U;
}

void *open_cfw_bootloader_tlsf_block_to_pointer_416a9c(
    const open_cfw_bootloader_tlsf_allocator_block *block)
{
    return (void *)((uintptr_t)block + 8U);
}

open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_offset_to_block_416aa6(
    const void *pointer,
    open_cfw_bootloader_tlsf_allocator_size offset)
{
    if (open_cfw_test_remaining != NULL) {
        return open_cfw_test_remaining;
    }
    return (open_cfw_bootloader_tlsf_allocator_block *)(
        (uintptr_t)pointer + offset);
}

open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_prev_416aaa(
    const open_cfw_bootloader_tlsf_allocator_block *block)
{
    return block->previous_physical_block;
}

open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_next_416ad0(
    const open_cfw_bootloader_tlsf_allocator_block *block)
{
    if (block == open_cfw_test_primary) {
        if (open_cfw_bootloader_tlsf_block_size_4169fc(block) >= 64U &&
            open_cfw_test_trailing != NULL) {
            return open_cfw_test_trailing;
        }
        return open_cfw_test_remaining != NULL
            ? open_cfw_test_remaining : open_cfw_test_trailing;
    }
    if (block == open_cfw_test_remaining) {
        return open_cfw_test_trailing;
    }
    return open_cfw_test_trailing;
}

open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_block_link_next_416b14(
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    open_cfw_bootloader_tlsf_allocator_block *next =
        open_cfw_bootloader_tlsf_block_next_416ad0(block);
    if (next != NULL) {
        next->previous_physical_block = block;
    }
    return next;
}

void open_cfw_bootloader_tlsf_block_mark_as_free_416b22(
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    open_cfw_bootloader_tlsf_allocator_block *next =
        open_cfw_bootloader_tlsf_block_link_next_416b14(block);
    if (next != NULL) {
        next->size |= 2U;
    }
    block->size |= 1U;
}

void open_cfw_bootloader_tlsf_block_mark_as_used_416b38(
    open_cfw_bootloader_tlsf_allocator_block *block)
{
    open_cfw_bootloader_tlsf_allocator_block *next =
        open_cfw_bootloader_tlsf_block_next_416ad0(block);
    if (next != NULL) {
        next->size &= ~2U;
    }
    block->size &= ~1U;
}

void *open_cfw_bootloader_tlsf_align_pointer_416ba4(
    const void *pointer,
    open_cfw_bootloader_tlsf_allocator_size alignment)
{
    return (void *)(((uintptr_t)pointer + alignment - 1U) &
        ~(uintptr_t)(alignment - 1U));
}

static unsigned int open_cfw_test_log2(unsigned int value)
{
    unsigned int result = 0U;
    while (value >>= 1U) {
        ++result;
    }
    return result;
}

void open_cfw_bootloader_tlsf_mapping_insert_416bf8(
    open_cfw_bootloader_tlsf_allocator_size size,
    int *first_level,
    int *second_level)
{
    if (size < 128U) {
        *first_level = 0;
        *second_level = (int)(size / 4U);
    } else {
        const int logarithm = (int)open_cfw_test_log2(size);
        *second_level = (int)(size >> (logarithm - 5)) ^ 32;
        *first_level = logarithm - 6;
    }
}

void open_cfw_bootloader_tlsf_mapping_search_416c26(
    open_cfw_bootloader_tlsf_allocator_size size,
    int *first_level,
    int *second_level)
{
    if (size >= 128U) {
        size += (1U << (open_cfw_test_log2(size) - 5U)) - 1U;
    }
    open_cfw_bootloader_tlsf_mapping_insert_416bf8(
        size,
        first_level,
        second_level);
}

open_cfw_bootloader_tlsf_allocator_block *
open_cfw_bootloader_tlsf_search_suitable_block_416c4e(
    open_cfw_bootloader_tlsf_allocator_control *control,
    int *first_level,
    int *second_level)
{
    unsigned int first = (unsigned int)*first_level;
    unsigned int second = (unsigned int)*second_level;
    unsigned int second_map =
        control->second_level_bitmap[first] & (~0U << second);
    if (second_map == 0U) {
        unsigned int first_map =
            control->first_level_bitmap & (~0U << (first + 1U));
        if (first_map == 0U) {
            return NULL;
        }
        first = (unsigned int)__builtin_ctz(first_map);
        *first_level = (int)first;
        second_map = control->second_level_bitmap[first];
    }
    second = (unsigned int)__builtin_ctz(second_map);
    *second_level = (int)second;
    return control->blocks[first][second];
}

void open_cfw_bootloader_tlsf_remove_free_block_416cc6(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block,
    int first,
    int second)
{
    open_cfw_bootloader_tlsf_allocator_block *previous =
        block->previous_free;
    open_cfw_bootloader_tlsf_allocator_block *next = block->next_free;
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

void open_cfw_bootloader_tlsf_insert_free_block_416d5c(
    open_cfw_bootloader_tlsf_allocator_control *control,
    open_cfw_bootloader_tlsf_allocator_block *block,
    int first,
    int second)
{
    open_cfw_bootloader_tlsf_allocator_block *current =
        control->blocks[first][second];
    block->next_free = current;
    block->previous_free = &control->block_null;
    current->previous_free = block;
    control->blocks[first][second] = block;
    control->first_level_bitmap |= 1U << first;
    control->second_level_bitmap[first] |= 1U << second;
}

static void open_cfw_test_reset(
    open_cfw_bootloader_tlsf_allocator_control *control)
{
    unsigned int first;
    unsigned int second;
    memset(control, 0, sizeof(*control));
    control->block_null.next_free = &control->block_null;
    control->block_null.previous_free = &control->block_null;
    for (first = 0U; first < 24U; ++first) {
        for (second = 0U; second < 32U; ++second) {
            control->blocks[first][second] = &control->block_null;
        }
    }
    open_cfw_test_assert_count = 0U;
    open_cfw_test_assert_expression = 0U;
    open_cfw_test_assert_line = 0U;
    open_cfw_test_primary = NULL;
    open_cfw_test_remaining = NULL;
    open_cfw_test_trailing = NULL;
}

unsigned int open_cfw_test_tlsf_allocator_insert_remove(void)
{
    open_cfw_bootloader_tlsf_allocator_control control;
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    open_cfw_test_reset(&control);
    block.size = 64U | 1U;
    open_cfw_bootloader_tlsf_block_insert_416e26(&control, &block);
    if (control.blocks[0][16] != &block ||
        control.first_level_bitmap != 1U ||
        control.second_level_bitmap[0] != (1U << 16)) {
        return 0U;
    }
    open_cfw_bootloader_tlsf_block_remove_416e04(&control, &block);
    return control.blocks[0][16] == &control.block_null &&
        control.first_level_bitmap == 0U &&
        control.second_level_bitmap[0] == 0U;
}

unsigned int open_cfw_test_tlsf_allocator_can_split(void)
{
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    block.size = 64U | 1U;
    return
        !open_cfw_bootloader_tlsf_block_can_split_416e48(&block, 49U) &&
        open_cfw_bootloader_tlsf_block_can_split_416e48(&block, 48U);
}

unsigned int open_cfw_test_tlsf_allocator_split(void)
{
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    open_cfw_bootloader_tlsf_allocator_block remaining = {0};
    open_cfw_bootloader_tlsf_allocator_block trailing = {0};
    open_cfw_bootloader_tlsf_allocator_block *result;
    open_cfw_test_assert_count = 0U;
    open_cfw_test_primary = &block;
    open_cfw_test_remaining = &remaining;
    open_cfw_test_trailing = &trailing;
    block.size = 96U | 1U;
    result = open_cfw_bootloader_tlsf_block_split_416e60(&block, 40U);
    return result == &remaining && (block.size & ~3U) == 40U &&
        (remaining.size & ~3U) == 52U && (remaining.size & 1U) != 0U &&
        trailing.previous_physical_block == &remaining &&
        (trailing.size & 2U) != 0U && open_cfw_test_assert_count == 0U;
}

unsigned int open_cfw_test_tlsf_allocator_absorb(void)
{
    open_cfw_bootloader_tlsf_allocator_block previous = {0};
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    open_cfw_bootloader_tlsf_allocator_block trailing = {0};
    open_cfw_test_assert_count = 0U;
    open_cfw_test_primary = &previous;
    open_cfw_test_remaining = NULL;
    open_cfw_test_trailing = &trailing;
    previous.size = 40U | 3U;
    block.size = 20U | 1U;
    return open_cfw_bootloader_tlsf_block_absorb_416f20(
            &previous, &block) == &previous &&
        (previous.size & ~3U) == 64U && (previous.size & 3U) == 3U &&
        trailing.previous_physical_block == &previous &&
        open_cfw_test_assert_count == 0U;
}

unsigned int open_cfw_test_tlsf_allocator_merge_previous(void)
{
    open_cfw_bootloader_tlsf_allocator_control control;
    open_cfw_bootloader_tlsf_allocator_block previous = {0};
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    open_cfw_bootloader_tlsf_allocator_block trailing = {0};
    open_cfw_bootloader_tlsf_allocator_block *result;
    open_cfw_test_reset(&control);
    previous.size = 40U | 1U;
    block.size = 20U | 3U;
    block.previous_physical_block = &previous;
    open_cfw_bootloader_tlsf_block_insert_416e26(&control, &previous);
    open_cfw_test_primary = &previous;
    open_cfw_test_trailing = &trailing;
    result = open_cfw_bootloader_tlsf_block_merge_previous_416f62(
        &control, &block);
    return result == &previous && (previous.size & ~3U) == 64U &&
        control.first_level_bitmap == 0U &&
        trailing.previous_physical_block == &previous &&
        open_cfw_test_assert_count == 0U;
}

unsigned int open_cfw_test_tlsf_allocator_merge_next(void)
{
    open_cfw_bootloader_tlsf_allocator_control control;
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    open_cfw_bootloader_tlsf_allocator_block next = {0};
    open_cfw_bootloader_tlsf_allocator_block trailing = {0};
    open_cfw_bootloader_tlsf_allocator_block *result;
    open_cfw_test_reset(&control);
    block.size = 40U | 1U;
    next.size = 20U | 1U;
    open_cfw_bootloader_tlsf_block_insert_416e26(&control, &next);
    open_cfw_test_primary = &block;
    open_cfw_test_remaining = &next;
    open_cfw_test_trailing = &trailing;
    result = open_cfw_bootloader_tlsf_block_merge_next_416fc6(
        &control, &block);
    return result == &block && (block.size & ~3U) == 64U &&
        control.first_level_bitmap == 0U &&
        trailing.previous_physical_block == &block &&
        open_cfw_test_assert_count == 0U;
}

unsigned int open_cfw_test_tlsf_allocator_trim_locate_prepare(void)
{
    open_cfw_bootloader_tlsf_allocator_control control;
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    open_cfw_bootloader_tlsf_allocator_block remaining = {0};
    open_cfw_bootloader_tlsf_allocator_block trailing = {0};
    void *pointer;
    open_cfw_test_reset(&control);
    block.size = 96U | 1U;
    open_cfw_bootloader_tlsf_block_insert_416e26(&control, &block);
    if (open_cfw_bootloader_tlsf_block_locate_free_41707c(
            &control, 40U) != &block || control.first_level_bitmap != 0U) {
        return 0U;
    }
    open_cfw_test_primary = &block;
    open_cfw_test_remaining = &remaining;
    open_cfw_test_trailing = &trailing;
    pointer = open_cfw_bootloader_tlsf_block_prepare_used_4170de(
        &control, &block, 40U);
    return pointer == open_cfw_bootloader_tlsf_block_to_pointer_416a9c(&block) &&
        (block.size & ~3U) == 40U && (block.size & 1U) == 0U &&
        (remaining.size & ~3U) == 52U && (remaining.size & 1U) != 0U &&
        control.first_level_bitmap != 0U &&
        open_cfw_test_assert_count == 0U;
}

unsigned int open_cfw_test_tlsf_allocator_assert_contract(void)
{
    open_cfw_bootloader_tlsf_allocator_control control;
    open_cfw_bootloader_tlsf_allocator_block block = {0};
    open_cfw_test_reset(&control);
    block.size = 40U;
    open_cfw_bootloader_tlsf_block_trim_free_41702a(&control, &block, 40U);
    return open_cfw_test_assert_count == 1U &&
        open_cfw_test_assert_expression == 0x004325C8U &&
        open_cfw_test_assert_line == 713U;
}
