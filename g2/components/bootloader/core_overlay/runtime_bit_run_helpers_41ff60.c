/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 bootloader bit-run helpers.
 */

typedef __UINT8_TYPE__ open_cfw_bit_run_u8;
typedef __UINT32_TYPE__ open_cfw_bit_run_u32;

__attribute__((used, noinline))
open_cfw_bit_run_u32 open_cfw_bootloader_longest_ones_run_41ff60(
    const open_cfw_bit_run_u32 *word)
{
    open_cfw_bit_run_u32 value = *word;
    open_cfw_bit_run_u32 length = 0U;

    while (value != 0U) {
        value &= value << 1U;
        ++length;
    }

    return length;
}

__attribute__((used, noinline))
open_cfw_bit_run_u32 open_cfw_bootloader_longest_ones_center_41ff74(
    const open_cfw_bit_run_u32 *word)
{
    const open_cfw_bit_run_u32 value = *word;
    open_cfw_bit_run_u32 current_length = 0U;
    open_cfw_bit_run_u32 best_length = 0U;
    open_cfw_bit_run_u32 center = 0U;
    open_cfw_bit_run_u8 in_run = 0U;
    open_cfw_bit_run_u8 best_length_odd = 0U;
    open_cfw_bit_run_u8 finish_run = 0U;
    open_cfw_bit_run_u32 bit;

    for (bit = 0U; bit < 32U; ++bit) {
        if (((value >> bit) & 1U) != 0U) {
            in_run = 1U;
            ++current_length;
        } else if (in_run != 0U) {
            in_run = 0U;
            finish_run = 1U;
        }

        if (bit == 31U && in_run != 0U) {
            finish_run = 1U;
        }

        if (finish_run != 0U) {
            if (best_length < current_length) {
                best_length = current_length;
                center = (bit - 1U) - (current_length >> 1U);
                best_length_odd = (open_cfw_bit_run_u8)(current_length & 1U);
            }
            current_length = 0U;
            finish_run = 0U;
        }
    }

    if (center < 16U) {
        if ((value & (1UL << 1U)) != 0U) {
            center -= best_length_odd;
        }
    } else if ((value & (1UL << 30U)) != 0U) {
        ++center;
    }

    return center;
}
