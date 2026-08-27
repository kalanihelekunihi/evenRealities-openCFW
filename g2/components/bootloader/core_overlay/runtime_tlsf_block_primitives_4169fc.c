/*
 * Copyright (c) 2006-2016, Matthew Conte
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded freestanding adaptation of the TLSF v3.1 block-header primitives.
 */

typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_word;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_tlsf_uintptr;
typedef __SIZE_TYPE__ open_cfw_bootloader_tlsf_size;

typedef struct open_cfw_bootloader_tlsf_block {
    open_cfw_bootloader_tlsf_word previous_physical_block;
    open_cfw_bootloader_tlsf_word size;
    open_cfw_bootloader_tlsf_word next_free;
    open_cfw_bootloader_tlsf_word previous_free;
} open_cfw_bootloader_tlsf_block;

enum {
    OPEN_CFW_BOOTLOADER_TLSF_FREE_BIT = 1U,
    OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_FREE_BIT = 2U,
    OPEN_CFW_BOOTLOADER_TLSF_BLOCK_START_OFFSET = 8U
};

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_word
open_cfw_bootloader_tlsf_block_size_4169fc(
    const open_cfw_bootloader_tlsf_block *block)
{
    return block->size &
        ~(OPEN_CFW_BOOTLOADER_TLSF_FREE_BIT |
          OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_FREE_BIT);
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_set_size_416a10(
    open_cfw_bootloader_tlsf_block *block,
    open_cfw_bootloader_tlsf_word size)
{
    const open_cfw_bootloader_tlsf_word old_size = block->size;
    block->size = size |
        (old_size &
         (OPEN_CFW_BOOTLOADER_TLSF_FREE_BIT |
          OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_FREE_BIT));
}

__attribute__((used, noinline))
int open_cfw_bootloader_tlsf_block_is_last_416a2c(
    const open_cfw_bootloader_tlsf_block *block)
{
    return (block->size &
            ~(OPEN_CFW_BOOTLOADER_TLSF_FREE_BIT |
              OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_FREE_BIT)) == 0U;
}

__attribute__((used, noinline))
int open_cfw_bootloader_tlsf_block_is_free_416a40(
    const open_cfw_bootloader_tlsf_block *block)
{
    return (int)(block->size & OPEN_CFW_BOOTLOADER_TLSF_FREE_BIT);
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_set_free_416a4c(
    open_cfw_bootloader_tlsf_block *block)
{
    block->size |= OPEN_CFW_BOOTLOADER_TLSF_FREE_BIT;
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_set_used_416a5a(
    open_cfw_bootloader_tlsf_block *block)
{
    block->size &= ~OPEN_CFW_BOOTLOADER_TLSF_FREE_BIT;
}

__attribute__((used, noinline))
int open_cfw_bootloader_tlsf_block_is_previous_free_416a68(
    const open_cfw_bootloader_tlsf_block *block)
{
    return (int)(block->size & OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_FREE_BIT);
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_set_previous_free_416a74(
    open_cfw_bootloader_tlsf_block *block)
{
    block->size |= OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_FREE_BIT;
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_set_previous_used_416a82(
    open_cfw_bootloader_tlsf_block *block)
{
    block->size &= ~OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_FREE_BIT;
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_block *
open_cfw_bootloader_tlsf_block_from_pointer_416a90(const void *pointer)
{
    return (open_cfw_bootloader_tlsf_block *)(open_cfw_bootloader_tlsf_uintptr)(
        (open_cfw_bootloader_tlsf_uintptr)pointer -
        OPEN_CFW_BOOTLOADER_TLSF_BLOCK_START_OFFSET);
}

__attribute__((used, noinline))
void *open_cfw_bootloader_tlsf_block_to_pointer_416a9c(
    const open_cfw_bootloader_tlsf_block *block)
{
    return (void *)(open_cfw_bootloader_tlsf_uintptr)(
        (open_cfw_bootloader_tlsf_uintptr)block +
        OPEN_CFW_BOOTLOADER_TLSF_BLOCK_START_OFFSET);
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_block *
open_cfw_bootloader_tlsf_offset_to_block_416aa6(
    const void *pointer,
    open_cfw_bootloader_tlsf_size offset)
{
    return (open_cfw_bootloader_tlsf_block *)(open_cfw_bootloader_tlsf_uintptr)(
        (open_cfw_bootloader_tlsf_uintptr)pointer + offset);
}
