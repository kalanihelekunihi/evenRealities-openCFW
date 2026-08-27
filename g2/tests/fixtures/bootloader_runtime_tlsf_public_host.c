#include <stdint.h>
#include <stddef.h>

#define OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_HOST 1
#include "../../components/bootloader/core_overlay/runtime_tlsf_public_41711c.c"

static open_cfw_bootloader_tlsf_public_block pool_block;
static open_cfw_bootloader_tlsf_public_block pool_sentinel;
static open_cfw_bootloader_tlsf_public_block allocation_block;
static unsigned char allocation_result;
static unsigned insert_calls;
static unsigned locate_calls;
static unsigned prepare_calls;
static unsigned free_mark_calls;
static unsigned merge_previous_calls;
static unsigned merge_next_calls;
static unsigned assertion_calls;
static open_cfw_bootloader_tlsf_public_word last_expression;
static open_cfw_bootloader_tlsf_public_word last_line;
static unsigned log_calls;
static open_cfw_bootloader_tlsf_public_word last_format;
static open_cfw_bootloader_tlsf_public_word last_log_first;
static open_cfw_bootloader_tlsf_public_word last_log_second;

static void reset_state(void)
{
    pool_block.previous_physical_block = 0;
    pool_block.size = 0;
    pool_block.next_free = 0;
    pool_block.previous_free = 0;
    pool_sentinel.previous_physical_block = 0;
    pool_sentinel.size = 0;
    pool_sentinel.next_free = 0;
    pool_sentinel.previous_free = 0;
    allocation_block.previous_physical_block = 0;
    allocation_block.size = 0;
    allocation_block.next_free = 0;
    allocation_block.previous_free = 0;
    insert_calls = 0;
    locate_calls = 0;
    prepare_calls = 0;
    free_mark_calls = 0;
    merge_previous_calls = 0;
    merge_next_calls = 0;
    assertion_calls = 0;
    last_expression = 0;
    last_line = 0;
    log_calls = 0;
    last_format = 0;
    last_log_first = 0;
    last_log_second = 0;
}

open_cfw_bootloader_tlsf_public_size
open_cfw_bootloader_tlsf_align_down_416b7a(
    open_cfw_bootloader_tlsf_public_size value,
    open_cfw_bootloader_tlsf_public_size alignment)
{
    return value & ~(alignment - 1U);
}

open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_offset_to_block_416aa6(
    const void *pointer,
    open_cfw_bootloader_tlsf_public_size offset)
{
    (void)pointer;
    (void)offset;
    return &pool_block;
}

void open_cfw_bootloader_tlsf_block_set_size_416a10(
    open_cfw_bootloader_tlsf_public_block *block,
    open_cfw_bootloader_tlsf_public_word size)
{
    block->size = size | (block->size & 3U);
}

void open_cfw_bootloader_tlsf_block_set_free_416a4c(
    open_cfw_bootloader_tlsf_public_block *block)
{
    block->size |= 1U;
}

void open_cfw_bootloader_tlsf_block_set_used_416a5a(
    open_cfw_bootloader_tlsf_public_block *block)
{
    block->size &= ~1U;
}

void open_cfw_bootloader_tlsf_block_set_previous_free_416a74(
    open_cfw_bootloader_tlsf_public_block *block)
{
    block->size |= 2U;
}

void open_cfw_bootloader_tlsf_block_set_previous_used_416a82(
    open_cfw_bootloader_tlsf_public_block *block)
{
    block->size &= ~2U;
}

open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_from_pointer_416a90(const void *pointer)
{
    (void)pointer;
    return &allocation_block;
}

open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_link_next_416b14(
    open_cfw_bootloader_tlsf_public_block *block)
{
    (void)block;
    return &pool_sentinel;
}

open_cfw_bootloader_tlsf_public_size
open_cfw_bootloader_tlsf_adjust_request_size_416bce(
    open_cfw_bootloader_tlsf_public_size size,
    open_cfw_bootloader_tlsf_public_size alignment)
{
    const open_cfw_bootloader_tlsf_public_size aligned =
        (size + alignment - 1U) & ~(alignment - 1U);
    if (size == 0U || aligned >= OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MAX) {
        return 0U;
    }
    return aligned < OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MIN ?
        OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_BLOCK_SIZE_MIN : aligned;
}

int open_cfw_bootloader_tlsf_block_is_free_416a40(
    const open_cfw_bootloader_tlsf_public_block *block)
{
    return (int)(block->size & 1U);
}

void open_cfw_bootloader_tlsf_block_insert_416e26(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block)
{
    (void)control;
    (void)block;
    ++insert_calls;
}

open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_locate_free_41707c(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_size size)
{
    (void)control;
    ++locate_calls;
    return size == 0U ? 0 : &allocation_block;
}

void *open_cfw_bootloader_tlsf_block_prepare_used_4170de(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block,
    open_cfw_bootloader_tlsf_public_size size)
{
    (void)control;
    ++prepare_calls;
    return block != 0 && size != 0U ? &allocation_result : 0;
}

void open_cfw_bootloader_tlsf_block_mark_as_free_416b22(
    open_cfw_bootloader_tlsf_public_block *block)
{
    ++free_mark_calls;
    block->size |= 1U;
}

open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_merge_previous_416f62(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block)
{
    (void)control;
    ++merge_previous_calls;
    return block;
}

open_cfw_bootloader_tlsf_public_block *
open_cfw_bootloader_tlsf_block_merge_next_416fc6(
    open_cfw_bootloader_tlsf_public_control *control,
    open_cfw_bootloader_tlsf_public_block *block)
{
    (void)control;
    ++merge_next_calls;
    return block;
}

void open_cfw_bootloader_tlsf_public_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_public_word line)
{
    ++assertion_calls;
    last_expression = (open_cfw_bootloader_tlsf_public_word)(uintptr_t)expression;
    last_line = line;
    if ((open_cfw_bootloader_tlsf_public_word)(uintptr_t)file !=
            OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FILE_ADDRESS) {
        assertion_calls += 100U;
    }
}

void open_cfw_bootloader_tlsf_public_host_log(
    const char *format,
    open_cfw_bootloader_tlsf_public_word first,
    open_cfw_bootloader_tlsf_public_word second)
{
    ++log_calls;
    last_format = (open_cfw_bootloader_tlsf_public_word)(uintptr_t)format;
    last_log_first = first;
    last_log_second = second;
}

unsigned open_cfw_test_tlsf_public_construct(void)
{
    static open_cfw_bootloader_tlsf_public_control control;
    unsigned first;
    unsigned second;
    reset_state();
    open_cfw_bootloader_tlsf_control_construct_41711c(&control);
    if (control.block_null.next_free != &control.block_null ||
            control.block_null.previous_free != &control.block_null ||
            control.first_level_bitmap != 0U) {
        return 0U;
    }
    for (first = 0U; first < OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_FL_INDEX_COUNT; ++first) {
        if (control.second_level_bitmap[first] != 0U) {
            return 0U;
        }
        for (second = 0U; second < OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_SL_INDEX_COUNT; ++second) {
            if (control.blocks[first][second] != &control.block_null) {
                return 0U;
            }
        }
    }
    return open_cfw_bootloader_tlsf_pool_overhead_41714c() == 8U;
}

unsigned open_cfw_test_tlsf_public_create_and_errors(void)
{
    static open_cfw_bootloader_tlsf_public_control control;
    reset_state();
    if (open_cfw_bootloader_tlsf_create_417208((void *)(uintptr_t)1U) != 0 ||
            log_calls != 1U ||
            last_format != OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CREATE_ALIGNMENT_FORMAT ||
            last_log_first != 4U) {
        return 0U;
    }
    if (open_cfw_bootloader_tlsf_create_417208(&control) != &control) {
        return 0U;
    }
    if (open_cfw_bootloader_tlsf_add_pool_41715c(
            &control, (void *)(uintptr_t)1U, 64U) != 0 ||
            log_calls != 2U ||
            last_format != OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ADD_POOL_ALIGNMENT_FORMAT) {
        return 0U;
    }
    if (open_cfw_bootloader_tlsf_add_pool_41715c(&control, &control, 8U) != 0 ||
            log_calls != 3U ||
            last_format != OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ADD_POOL_SIZE_FORMAT ||
            last_log_first != 20U ||
            last_log_second != 0x40000008U) {
        return 0U;
    }
    return 1U;
}

unsigned open_cfw_test_tlsf_public_add_pool(void)
{
    static open_cfw_bootloader_tlsf_public_control control;
    reset_state();
    if (open_cfw_bootloader_tlsf_add_pool_41715c(&control, &control, 72U) != &control) {
        return 0U;
    }
    return insert_calls == 1U && pool_block.size == 65U &&
        pool_sentinel.size == 2U;
}

unsigned open_cfw_test_tlsf_public_create_with_pool(void)
{
    static union {
        open_cfw_bootloader_tlsf_public_control align;
        unsigned char bytes[OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_CONTROL_SIZE + 128U];
    } memory;
    reset_state();
    return open_cfw_bootloader_tlsf_create_with_pool_417240(
        memory.bytes, sizeof(memory.bytes)) == memory.bytes && insert_calls == 1U;
}

unsigned open_cfw_test_tlsf_public_malloc(void)
{
    static open_cfw_bootloader_tlsf_public_control control;
    reset_state();
    if (open_cfw_bootloader_tlsf_malloc_41726a(&control, 5U) != &allocation_result ||
            locate_calls != 1U || prepare_calls != 1U) {
        return 0U;
    }
    if (open_cfw_bootloader_tlsf_malloc_41726a(&control, 0U) != 0 ||
            locate_calls != 2U || prepare_calls != 2U) {
        return 0U;
    }
    return 1U;
}

unsigned open_cfw_test_tlsf_public_free(void)
{
    static open_cfw_bootloader_tlsf_public_control control;
    reset_state();
    open_cfw_bootloader_tlsf_free_417290(&control, 0);
    if (free_mark_calls != 0U) {
        return 0U;
    }
    allocation_block.size = 20U;
    open_cfw_bootloader_tlsf_free_417290(&control, &allocation_result);
    if (assertion_calls != 0U || free_mark_calls != 1U ||
            merge_previous_calls != 1U || merge_next_calls != 1U ||
            insert_calls != 1U) {
        return 0U;
    }
    open_cfw_bootloader_tlsf_free_417290(&control, &allocation_result);
    return assertion_calls == 1U &&
        last_expression == OPEN_CFW_BOOTLOADER_TLSF_PUBLIC_ALREADY_FREE_ADDRESS &&
        last_line == 1188U;
}
