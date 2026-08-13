/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production source seams for the authenticated G2 EasyLogger
 * hexdump replacement.  The formatter implements only the three formats used
 * by elog_hexdump; the transport adapter preserves the G2 level-less record
 * ABI instead of pretending it is upstream EasyLogger.  Its ownership rule
 * is intentionally safer than stock: allocation transfers ownership to the
 * builder, and enqueue consumes it on both success and failure.
 */

#ifndef OPEN_CFW_RUNTIME_EASYLOGGER_HEXDUMP_SUPPORT_H
#define OPEN_CFW_RUNTIME_EASYLOGGER_HEXDUMP_SUPPORT_H

typedef __UINT8_TYPE__ open_cfw_easylogger_hexdump_seam_u8;
typedef __UINT16_TYPE__ open_cfw_easylogger_hexdump_seam_u16;
typedef __UINT32_TYPE__ open_cfw_easylogger_hexdump_seam_u32;

void open_cfw_easylogger_hexdump_put(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 size,
    open_cfw_easylogger_hexdump_seam_u32 *length,
    char value
);

void open_cfw_easylogger_hexdump_put_hex(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 size,
    open_cfw_easylogger_hexdump_seam_u32 *length,
    unsigned int value,
    unsigned int minimum_digits
);

void *open_cfw_easylogger_hexdump_fill(
    void *destination,
    open_cfw_easylogger_hexdump_seam_u32 count,
    open_cfw_easylogger_hexdump_seam_u32 value
);

int open_cfw_easylogger_hexdump_format_header(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 size,
    const char *name,
    unsigned int offset,
    unsigned int end
);

void open_cfw_easylogger_hexdump_format_hex(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u8 value
);

void open_cfw_easylogger_hexdump_format_character(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u8 value
);

void open_cfw_easylogger_hexdump_blank_hex(char *buffer);

open_cfw_easylogger_hexdump_seam_u32
open_cfw_g2_easylogger_async_record_build_level_less_single_owner(
    const char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 length,
    open_cfw_easylogger_hexdump_seam_u32 metadata
);

void open_cfw_easylogger_hexdump_raw_submit(
    const char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 length
);

#endif
