/*
 * Copyright (c) 2006-2016, Matthew Conte
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded freestanding adaptation of TLSF v3.1 physical-block and alignment
 * helpers for the authenticated G2 bootloader ILP32 ABI.
 */

typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_word;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_tlsf_uintptr;
typedef __SIZE_TYPE__ open_cfw_bootloader_tlsf_size;

#if defined(OPEN_CFW_BOOTLOADER_TLSF_TOPOLOGY_HOST)
typedef open_cfw_bootloader_tlsf_uintptr
    open_cfw_bootloader_tlsf_previous_word;
#else
typedef open_cfw_bootloader_tlsf_word
    open_cfw_bootloader_tlsf_previous_word;
#endif

typedef struct open_cfw_bootloader_tlsf_topology_block {
    open_cfw_bootloader_tlsf_previous_word previous_physical_block;
    open_cfw_bootloader_tlsf_word size;
    open_cfw_bootloader_tlsf_word next_free;
    open_cfw_bootloader_tlsf_word previous_free;
} open_cfw_bootloader_tlsf_topology_block;

typedef void (*open_cfw_bootloader_tlsf_assert_fn)(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_word line);

enum {
    OPEN_CFW_BOOTLOADER_TLSF_HEADER_OVERHEAD = 4U,
    OPEN_CFW_BOOTLOADER_TLSF_FILE_ADDRESS = 0x00431A04U,
    OPEN_CFW_BOOTLOADER_TLSF_ALIGN_EXPRESSION_ADDRESS = 0x0043188CU,
    OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_EXPRESSION_ADDRESS = 0x004319C8U,
    OPEN_CFW_BOOTLOADER_TLSF_LAST_EXPRESSION_ADDRESS = 0x00433A84U,
    OPEN_CFW_BOOTLOADER_TLSF_ASSERT_THUMB_ADDRESS = 0x00415735U
};

open_cfw_bootloader_tlsf_word
open_cfw_bootloader_tlsf_block_size_4169fc(
    const open_cfw_bootloader_tlsf_topology_block *block);
int open_cfw_bootloader_tlsf_block_is_last_416a2c(
    const open_cfw_bootloader_tlsf_topology_block *block);
void open_cfw_bootloader_tlsf_block_set_free_416a4c(
    open_cfw_bootloader_tlsf_topology_block *block);
void open_cfw_bootloader_tlsf_block_set_used_416a5a(
    open_cfw_bootloader_tlsf_topology_block *block);
int open_cfw_bootloader_tlsf_block_is_previous_free_416a68(
    const open_cfw_bootloader_tlsf_topology_block *block);
void open_cfw_bootloader_tlsf_block_set_previous_free_416a74(
    open_cfw_bootloader_tlsf_topology_block *block);
void open_cfw_bootloader_tlsf_block_set_previous_used_416a82(
    open_cfw_bootloader_tlsf_topology_block *block);
void *open_cfw_bootloader_tlsf_block_to_pointer_416a9c(
    const open_cfw_bootloader_tlsf_topology_block *block);
open_cfw_bootloader_tlsf_topology_block *
open_cfw_bootloader_tlsf_offset_to_block_416aa6(
    const void *pointer,
    open_cfw_bootloader_tlsf_size offset);

#if defined(OPEN_CFW_BOOTLOADER_TLSF_TOPOLOGY_HOST)
void open_cfw_bootloader_tlsf_topology_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_word line);
#endif

static __attribute__((always_inline)) inline void
open_cfw_bootloader_tlsf_require(
    int condition,
    open_cfw_bootloader_tlsf_word expression_address,
    open_cfw_bootloader_tlsf_word line)
{
    if (!condition) {
#if defined(OPEN_CFW_BOOTLOADER_TLSF_TOPOLOGY_HOST)
        open_cfw_bootloader_tlsf_topology_host_assert(
            (const char *)(open_cfw_bootloader_tlsf_uintptr)expression_address,
            (const char *)(open_cfw_bootloader_tlsf_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_FILE_ADDRESS,
            line);
#else
        ((open_cfw_bootloader_tlsf_assert_fn)
            (open_cfw_bootloader_tlsf_uintptr)
                OPEN_CFW_BOOTLOADER_TLSF_ASSERT_THUMB_ADDRESS)(
                    (const char *)(open_cfw_bootloader_tlsf_uintptr)
                        expression_address,
                    (const char *)(open_cfw_bootloader_tlsf_uintptr)
                        OPEN_CFW_BOOTLOADER_TLSF_FILE_ADDRESS,
                    line);
#endif
    }
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_topology_block *
open_cfw_bootloader_tlsf_block_prev_416aaa(
    const open_cfw_bootloader_tlsf_topology_block *block)
{
    open_cfw_bootloader_tlsf_require(
        open_cfw_bootloader_tlsf_block_is_previous_free_416a68(block),
        OPEN_CFW_BOOTLOADER_TLSF_PREVIOUS_EXPRESSION_ADDRESS,
        433U);
    return (open_cfw_bootloader_tlsf_topology_block *)
        (open_cfw_bootloader_tlsf_uintptr)block->previous_physical_block;
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_topology_block *
open_cfw_bootloader_tlsf_block_next_416ad0(
    const open_cfw_bootloader_tlsf_topology_block *block)
{
    const open_cfw_bootloader_tlsf_word size =
        open_cfw_bootloader_tlsf_block_size_4169fc(block);
    void *pointer = open_cfw_bootloader_tlsf_block_to_pointer_416a9c(block);
    open_cfw_bootloader_tlsf_topology_block *next =
        open_cfw_bootloader_tlsf_offset_to_block_416aa6(
            pointer,
            (open_cfw_bootloader_tlsf_size)(
                size - OPEN_CFW_BOOTLOADER_TLSF_HEADER_OVERHEAD));
    open_cfw_bootloader_tlsf_require(
        !open_cfw_bootloader_tlsf_block_is_last_416a2c(block),
        OPEN_CFW_BOOTLOADER_TLSF_LAST_EXPRESSION_ADDRESS,
        442U);
    return next;
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_topology_block *
open_cfw_bootloader_tlsf_block_link_next_416b14(
    open_cfw_bootloader_tlsf_topology_block *block)
{
    open_cfw_bootloader_tlsf_topology_block *next =
        open_cfw_bootloader_tlsf_block_next_416ad0(block);
    next->previous_physical_block =
        (open_cfw_bootloader_tlsf_previous_word)
            (open_cfw_bootloader_tlsf_uintptr)block;
    return next;
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_mark_as_free_416b22(
    open_cfw_bootloader_tlsf_topology_block *block)
{
    open_cfw_bootloader_tlsf_topology_block *next =
        open_cfw_bootloader_tlsf_block_link_next_416b14(block);
    open_cfw_bootloader_tlsf_block_set_previous_free_416a74(next);
    open_cfw_bootloader_tlsf_block_set_free_416a4c(block);
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_block_mark_as_used_416b38(
    open_cfw_bootloader_tlsf_topology_block *block)
{
    open_cfw_bootloader_tlsf_topology_block *next =
        open_cfw_bootloader_tlsf_block_next_416ad0(block);
    open_cfw_bootloader_tlsf_block_set_previous_used_416a82(next);
    open_cfw_bootloader_tlsf_block_set_used_416a5a(block);
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_size open_cfw_bootloader_tlsf_align_up_416b4e(
    open_cfw_bootloader_tlsf_size value,
    open_cfw_bootloader_tlsf_size alignment)
{
    open_cfw_bootloader_tlsf_require(
        (alignment & (alignment - 1U)) == 0U,
        OPEN_CFW_BOOTLOADER_TLSF_ALIGN_EXPRESSION_ADDRESS,
        471U);
    return (value + (alignment - 1U)) & ~(alignment - 1U);
}

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_size open_cfw_bootloader_tlsf_align_down_416b7a(
    open_cfw_bootloader_tlsf_size value,
    open_cfw_bootloader_tlsf_size alignment)
{
    open_cfw_bootloader_tlsf_require(
        (alignment & (alignment - 1U)) == 0U,
        OPEN_CFW_BOOTLOADER_TLSF_ALIGN_EXPRESSION_ADDRESS,
        477U);
    return value - (value & (alignment - 1U));
}

__attribute__((used, noinline))
void *open_cfw_bootloader_tlsf_align_pointer_416ba4(
    const void *pointer,
    open_cfw_bootloader_tlsf_size alignment)
{
    const open_cfw_bootloader_tlsf_uintptr aligned =
        ((open_cfw_bootloader_tlsf_uintptr)pointer + (alignment - 1U)) &
        ~(open_cfw_bootloader_tlsf_uintptr)(alignment - 1U);
    open_cfw_bootloader_tlsf_require(
        (alignment & (alignment - 1U)) == 0U,
        OPEN_CFW_BOOTLOADER_TLSF_ALIGN_EXPRESSION_ADDRESS,
        485U);
    return (void *)aligned;
}
