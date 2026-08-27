#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_BOOTLOADER_TLSF_TOPOLOGY_HOST 1
#include "../../components/bootloader/core_overlay/runtime_tlsf_block_topology_416aaa.c"

static unsigned int open_cfw_test_assert_count;
static uintptr_t open_cfw_test_assert_expression;
static uintptr_t open_cfw_test_assert_file;
static unsigned int open_cfw_test_assert_line;

void open_cfw_bootloader_tlsf_topology_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_word line)
{
    ++open_cfw_test_assert_count;
    open_cfw_test_assert_expression = (uintptr_t)expression;
    open_cfw_test_assert_file = (uintptr_t)file;
    open_cfw_test_assert_line = line;
}

open_cfw_bootloader_tlsf_word
open_cfw_bootloader_tlsf_block_size_4169fc(
    const open_cfw_bootloader_tlsf_topology_block *block)
{
    return block->size & ~3U;
}

int open_cfw_bootloader_tlsf_block_is_last_416a2c(
    const open_cfw_bootloader_tlsf_topology_block *block)
{
    return (block->size & ~3U) == 0U;
}

void open_cfw_bootloader_tlsf_block_set_free_416a4c(
    open_cfw_bootloader_tlsf_topology_block *block)
{
    block->size |= 1U;
}

void open_cfw_bootloader_tlsf_block_set_used_416a5a(
    open_cfw_bootloader_tlsf_topology_block *block)
{
    block->size &= ~1U;
}

int open_cfw_bootloader_tlsf_block_is_previous_free_416a68(
    const open_cfw_bootloader_tlsf_topology_block *block)
{
    return (int)(block->size & 2U);
}

void open_cfw_bootloader_tlsf_block_set_previous_free_416a74(
    open_cfw_bootloader_tlsf_topology_block *block)
{
    block->size |= 2U;
}

void open_cfw_bootloader_tlsf_block_set_previous_used_416a82(
    open_cfw_bootloader_tlsf_topology_block *block)
{
    block->size &= ~2U;
}

void *open_cfw_bootloader_tlsf_block_to_pointer_416a9c(
    const open_cfw_bootloader_tlsf_topology_block *block)
{
    return (void *)((uintptr_t)block + offsetof(
        open_cfw_bootloader_tlsf_topology_block, size) + sizeof(uint32_t));
}

open_cfw_bootloader_tlsf_topology_block *
open_cfw_bootloader_tlsf_offset_to_block_416aa6(
    const void *pointer,
    open_cfw_bootloader_tlsf_size offset)
{
    return (open_cfw_bootloader_tlsf_topology_block *)
        ((uintptr_t)pointer + offset);
}

void open_cfw_test_tlsf_topology_reset_assert(void)
{
    open_cfw_test_assert_count = 0U;
    open_cfw_test_assert_expression = 0U;
    open_cfw_test_assert_file = 0U;
    open_cfw_test_assert_line = 0U;
}

unsigned int open_cfw_test_tlsf_topology_assert_count(void)
{
    return open_cfw_test_assert_count;
}

uintptr_t open_cfw_test_tlsf_topology_assert_expression(void)
{
    return open_cfw_test_assert_expression;
}

uintptr_t open_cfw_test_tlsf_topology_assert_file(void)
{
    return open_cfw_test_assert_file;
}

unsigned int open_cfw_test_tlsf_topology_assert_line(void)
{
    return open_cfw_test_assert_line;
}
