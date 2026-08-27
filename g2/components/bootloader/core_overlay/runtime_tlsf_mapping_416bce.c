/*
 * Copyright (c) 2006-2016, Matthew Conte
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded freestanding adaptation of TLSF v3.1 request-size and class
 * mapping helpers for the authenticated G2 bootloader ILP32 ABI.
 */

typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_mapping_word;
typedef __UINT32_TYPE__ open_cfw_bootloader_tlsf_mapping_size;

enum {
    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_BLOCK_SIZE_MIN = 12U,
    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_BLOCK_SIZE_MAX = 0x40000000U,
    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SMALL_BLOCK_SIZE = 128U,
    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SMALL_DIVISOR = 4U,
    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SL_INDEX_COUNT = 32U,
    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SL_INDEX_LOG2 = 5U,
    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_FL_INDEX_SHIFT = 7U
};

open_cfw_bootloader_tlsf_mapping_size
open_cfw_bootloader_tlsf_align_up_416b4e(
    open_cfw_bootloader_tlsf_mapping_size value,
    open_cfw_bootloader_tlsf_mapping_size alignment);

open_cfw_bootloader_tlsf_mapping_word
open_cfw_bootloader_runtime_log2_4169f2(
    open_cfw_bootloader_tlsf_mapping_word value);

__attribute__((used, noinline))
open_cfw_bootloader_tlsf_mapping_size
open_cfw_bootloader_tlsf_adjust_request_size_416bce(
    open_cfw_bootloader_tlsf_mapping_size size,
    open_cfw_bootloader_tlsf_mapping_size alignment)
{
    open_cfw_bootloader_tlsf_mapping_size adjusted = 0U;

    if (size != 0U) {
        const open_cfw_bootloader_tlsf_mapping_size aligned =
            open_cfw_bootloader_tlsf_align_up_416b4e(size, alignment);

        if (aligned < OPEN_CFW_BOOTLOADER_TLSF_MAPPING_BLOCK_SIZE_MAX) {
            adjusted =
                aligned > OPEN_CFW_BOOTLOADER_TLSF_MAPPING_BLOCK_SIZE_MIN
                    ? aligned
                    : OPEN_CFW_BOOTLOADER_TLSF_MAPPING_BLOCK_SIZE_MIN;
        }
    }

    return adjusted;
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_mapping_insert_416bf8(
    open_cfw_bootloader_tlsf_mapping_size size,
    int *first_level,
    int *second_level)
{
    int first;
    int second;

    if (size < OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SMALL_BLOCK_SIZE) {
        first = 0;
        second = (int)(size /
            OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SMALL_DIVISOR);
    } else {
        first = (int)open_cfw_bootloader_runtime_log2_4169f2(
            (open_cfw_bootloader_tlsf_mapping_word)size);
        second = (int)(size >>
            (first - OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SL_INDEX_LOG2)) ^
            OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SL_INDEX_COUNT;
        first -= OPEN_CFW_BOOTLOADER_TLSF_MAPPING_FL_INDEX_SHIFT - 1;
    }

    *first_level = first;
    *second_level = second;
}

__attribute__((used, noinline))
void open_cfw_bootloader_tlsf_mapping_search_416c26(
    open_cfw_bootloader_tlsf_mapping_size size,
    int *first_level,
    int *second_level)
{
    if (size >= OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SMALL_BLOCK_SIZE) {
        const open_cfw_bootloader_tlsf_mapping_word logarithm =
            open_cfw_bootloader_runtime_log2_4169f2(
                (open_cfw_bootloader_tlsf_mapping_word)size);
        const open_cfw_bootloader_tlsf_mapping_size round =
            ((open_cfw_bootloader_tlsf_mapping_size)1U <<
                (logarithm -
                    OPEN_CFW_BOOTLOADER_TLSF_MAPPING_SL_INDEX_LOG2)) - 1U;
        size += round;
    }

    open_cfw_bootloader_tlsf_mapping_insert_416bf8(
        size,
        first_level,
        second_level);
}
