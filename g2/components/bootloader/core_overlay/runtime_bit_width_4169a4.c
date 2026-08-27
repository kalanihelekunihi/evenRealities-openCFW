/* SPDX-License-Identifier: GPL-3.0-or-later */
typedef __UINT32_TYPE__ open_cfw_bootloader_bit_word;

__attribute__((used, noinline))
open_cfw_bootloader_bit_word
open_cfw_bootloader_runtime_bit_width_4169a4(
    open_cfw_bootloader_bit_word value)
{
    open_cfw_bootloader_bit_word width = 0U;
    while (value != 0U) {
        ++width;
        value >>= 1U;
    }
    return width;
}
