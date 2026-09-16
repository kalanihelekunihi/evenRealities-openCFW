/* SPDX-License-Identifier: MIT */
/* Upstream LVP diagnostic text and board/build configuration recovered from
 * the reviewed 2.2.6.10 image. Values are semantic source constants. */
#include <stdint.h>
#define TEXT(name, value) const char sys_##name[] __attribute__((section(".rodata.sys_" #name),aligned(1))) = value
/* The shipped diagnostics use LF line endings. */
TEXT(title, "[LVP]Low-Power Voice Preprocess\n");
TEXT(copyright, "[LVP]Copyright (C) 2001-2020 NationalChip Co., Ltd\n");
TEXT(rights, "[LVP]ALL RIGHTS RESERVED!\n");
TEXT(board, "grus_gx8002b_dev_1v");
TEXT(board_format, "[LVP]Board Model: [%s]\n");
TEXT(version, "");
TEXT(version_format, "[LVP]MCU Version: [%s]\n");
TEXT(release_format, "[LVP]Release Ver: [0x%x]\n");
TEXT(date, "2026-03-26, 17:07:19");
TEXT(date_format, "[LVP]Build Date : [%s]\n");
TEXT(puya, "PUYA");
TEXT(esmt, "ESMT");
TEXT(zbit, "ZBIT");
TEXT(vendor_format, "[LVP]Flash vendor:[%s]\n");
TEXT(type_format, "[LVP]Flash type:  [%s]\n");
TEXT(id_format, "[LVP]Flash ID:    [%#x]\n");
TEXT(size_format, "[LVP]Flash size:  [%d Byte]\n");
TEXT(cpu_format, "[LVP]CPU   Freq:  [%d Hz][fix]\n");
TEXT(sram_format, "[LVP]SRAM  Freq:  [%d Hz]\n");
TEXT(npu_format, "[LVP]NPU   Freq:  [%d Hz]\n");
TEXT(flash_format, "[LVP]FLASH Freq:  [%d Hz]\n");
TEXT(bypass, "[LVP]enable bypass core Ldo\n");
TEXT(trim_format, "[LVP]Ldo   Trim:  [%d mV]\n");
const int32_t sys_trim_millivolts[12] __attribute__((section(".rodata.sys_trim_millivolts"),aligned(4))) = {
    950,924,897,871,845,819,792,766,740,714,687,661
};
