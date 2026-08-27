/* SPDX-License-Identifier: GPL-3.0-or-later */
typedef __UINT32_TYPE__ open_cfw_bootloader_log2_word;

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_BIT_WIDTH_4169A4
extern open_cfw_bootloader_log2_word
open_cfw_bootloader_runtime_bit_width_4169a4(open_cfw_bootloader_log2_word);
#define OPEN_CFW_BOOTLOADER_RUNTIME_BIT_WIDTH_4169A4(value) \
    open_cfw_bootloader_runtime_bit_width_4169a4(value)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_log2_word
open_cfw_bootloader_runtime_log2_4169f2(open_cfw_bootloader_log2_word value)
{
    return OPEN_CFW_BOOTLOADER_RUNTIME_BIT_WIDTH_4169A4(value) - 1U;
}
