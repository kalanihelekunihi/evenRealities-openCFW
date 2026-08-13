/*
 * SPDX-License-Identifier: MIT
 *
 * Production Apollo-main ABI for the authenticated EasyLogger
 * elog_hexdump() replacement at [0x0043DACC,0x0043DC88), with dedicated
 * production overlay and firmware-manifest gates.
 */

#ifndef OPEN_CFW_RUNTIME_EASYLOGGER_HEXDUMP_H
#define OPEN_CFW_RUNTIME_EASYLOGGER_HEXDUMP_H

#include "runtime_easylogger_hexdump_support.h"

typedef __UINT8_TYPE__ open_cfw_easylogger_hexdump_u8;
typedef __UINT16_TYPE__ open_cfw_easylogger_hexdump_u16;
typedef __UINT32_TYPE__ open_cfw_easylogger_hexdump_u32;
typedef __UINTPTR_TYPE__ open_cfw_easylogger_hexdump_uintptr;

enum {
    OPEN_CFW_EASYLOGGER_HEXDUMP_LEVEL_DEBUG = 4,
    OPEN_CFW_EASYLOGGER_HEXDUMP_LEVEL_VERBOSE = 5,
    OPEN_CFW_EASYLOGGER_HEXDUMP_LINE_BUFFER_SIZE = 1024,
    OPEN_CFW_EASYLOGGER_HEXDUMP_TAG_MAX = 30,
    OPEN_CFW_EASYLOGGER_HEXDUMP_KEYWORD_MAX = 16,
    OPEN_CFW_EASYLOGGER_HEXDUMP_TAG_LEVEL_COUNT = 5,
    OPEN_CFW_EASYLOGGER_HEXDUMP_LEVEL_COUNT = 6,
    OPEN_CFW_EASYLOGGER_HEXDUMP_LOGGER_ADDRESS = 0x20070BE8U,
    OPEN_CFW_EASYLOGGER_HEXDUMP_BUFFER_ADDRESS = 0x2006BD30U
};

struct open_cfw_easylogger_hexdump_tag_level {
    open_cfw_easylogger_hexdump_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_HEXDUMP_TAG_MAX + 1];
    open_cfw_easylogger_hexdump_u8 tag_use_flag;
};

struct open_cfw_easylogger_hexdump_filter {
    open_cfw_easylogger_hexdump_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_HEXDUMP_TAG_MAX + 1];
    char keyword[OPEN_CFW_EASYLOGGER_HEXDUMP_KEYWORD_MAX + 1];
    struct open_cfw_easylogger_hexdump_tag_level
        tag_level[OPEN_CFW_EASYLOGGER_HEXDUMP_TAG_LEVEL_COUNT];
};

struct open_cfw_easylogger_hexdump_logger {
    struct open_cfw_easylogger_hexdump_filter filter;
    open_cfw_easylogger_hexdump_u32
        enabled_format_set[OPEN_CFW_EASYLOGGER_HEXDUMP_LEVEL_COUNT];
    open_cfw_easylogger_hexdump_u8 init_ok;
    open_cfw_easylogger_hexdump_u8 output_enabled;
    open_cfw_easylogger_hexdump_u8 output_lock_enabled;
    open_cfw_easylogger_hexdump_u8 output_is_locked_before_enable;
    open_cfw_easylogger_hexdump_u8 output_is_locked_before_disable;
    open_cfw_easylogger_hexdump_u8 text_color_enabled;
};

_Static_assert(
    sizeof(open_cfw_easylogger_hexdump_u16) == 2U,
    "G2 EasyLogger hexdump counter width changed"
);
_Static_assert(
    sizeof(open_cfw_easylogger_hexdump_u32) == 4U,
    "G2 EasyLogger size_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_hexdump_tag_level) == 0x21U,
    "G2 EasyLogger tag-level stride changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_hexdump_filter) == 0xD6U,
    "G2 EasyLogger filter layout changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_hexdump_logger,
        output_enabled
    ) == 0xF1U,
    "G2 EasyLogger output-enabled offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_hexdump_logger) == 0xF8U,
    "G2 EasyLogger object size changed"
);

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_GET_LOGGER
struct open_cfw_easylogger_helpers_logger;
struct open_cfw_easylogger_helpers_logger *
open_cfw_easylogger_helpers_get_logger(void);
#define OPEN_CFW_EASYLOGGER_HEXDUMP_GET_LOGGER() \
    ((struct open_cfw_easylogger_hexdump_logger *)(void *) \
        open_cfw_easylogger_helpers_get_logger())
#endif

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_GET_BUFFER
#define OPEN_CFW_EASYLOGGER_HEXDUMP_GET_BUFFER() \
    ((char *)(open_cfw_easylogger_hexdump_uintptr) \
        OPEN_CFW_EASYLOGGER_HEXDUMP_BUFFER_ADDRESS)
#endif

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_FILL
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FILL(destination, count, value) \
    open_cfw_easylogger_hexdump_fill((destination), (count), (value))
#endif

void open_cfw_easylogger_output_lock(void);
void open_cfw_easylogger_output_unlock(void);

open_cfw_easylogger_hexdump_u32 open_cfw_easylogger_strcpy(
    open_cfw_easylogger_hexdump_u32 current_length,
    char *destination,
    const char *source
);

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_RAW_SINK
#define OPEN_CFW_EASYLOGGER_HEXDUMP_RAW_SINK(buffer, length) \
    open_cfw_easylogger_hexdump_raw_submit((buffer), (length))
#endif

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEADER
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEADER( \
    buffer, size, name, offset, end \
) \
    open_cfw_easylogger_hexdump_format_header( \
        (buffer), (size), (name), (offset), (end) \
    )
#endif

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEX
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEX(buffer, value) \
    open_cfw_easylogger_hexdump_format_hex((buffer), (value))
#endif

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_CHARACTER
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_CHARACTER(buffer, value) \
    open_cfw_easylogger_hexdump_format_character((buffer), (value))
#endif

#ifndef OPEN_CFW_EASYLOGGER_HEXDUMP_BLANK_HEX
#define OPEN_CFW_EASYLOGGER_HEXDUMP_BLANK_HEX(buffer) \
    open_cfw_easylogger_hexdump_blank_hex((buffer))
#endif

void open_cfw_easylogger_hexdump(
    const char *name,
    open_cfw_easylogger_hexdump_u8 width,
    const void *buffer,
    open_cfw_easylogger_hexdump_u16 size
);

#endif
