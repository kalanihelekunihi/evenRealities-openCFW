/*
 * SPDX-License-Identifier: MIT
 *
 * Shared EasyLogger helper ABI for the Even Realities G2 Apollo-main and
 * bootloader images.
 *
 * The algorithms are adapted from the authenticated Armink EasyLogger
 * snapshot at commit a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24:
 *
 *   easylogger/src/elog_utils.c
 *     Git blob 165d855d2c8e8470b3543380ca6064c0799a8a44
 *   easylogger/src/elog.c
 *     Git blob b3a00e3927edf97013ddfffeb157be5c1462a6b4
 *
 * Focused G2 disassembly fixes the target ABI and the two image profiles.
 * State and assertion access remain explicit function seams so isolated
 * leaves contain only reviewed Thumb call relocations.
 */

#ifndef OPEN_CFW_RUNTIME_EASYLOGGER_HELPERS_H
#define OPEN_CFW_RUNTIME_EASYLOGGER_HELPERS_H

typedef __UINT8_TYPE__ open_cfw_easylogger_helpers_u8;
typedef __UINT32_TYPE__ open_cfw_easylogger_helpers_u32;
typedef __UINTPTR_TYPE__ open_cfw_easylogger_helpers_uintptr;

enum {
    OPEN_CFW_EASYLOGGER_HELPERS_LEVEL_VERBOSE = 5,
    OPEN_CFW_EASYLOGGER_HELPERS_LEVEL_COUNT = 6,
    OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE = 1024,
    OPEN_CFW_EASYLOGGER_HELPERS_TAG_MAX = 30,
    OPEN_CFW_EASYLOGGER_HELPERS_KEYWORD_MAX = 16,
    OPEN_CFW_EASYLOGGER_HELPERS_TAG_LEVEL_COUNT = 5,
    OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_DST_LINE = 44,
    OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_SRC_LINE = 45,
    OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_GET_FMT_LINE = 743
};

#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_APOLLO_MAIN 1
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER 2

#ifndef OPEN_CFW_EASYLOGGER_HELPERS_PROFILE
#error "select an explicit G2 EasyLogger image profile"
#endif

#if \
    OPEN_CFW_EASYLOGGER_HELPERS_PROFILE == \
        OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_APOLLO_MAIN
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS 0x20070BE8U
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_HOOK_ADDRESS 0x2007456CU
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_OUTPUT_ADDRESS 0x0043D574U
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_WAIT_ADDRESS 0x0044B0AEU
#elif \
    OPEN_CFW_EASYLOGGER_HELPERS_PROFILE == \
        OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS 0x20026700U
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_HOOK_ADDRESS 0x200270E4U
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_OUTPUT_ADDRESS 0x004176CEU
#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_WAIT_ADDRESS 0x0041AC8AU
#else
#error "unsupported G2 EasyLogger image profile"
#endif

struct open_cfw_easylogger_helpers_tag_level {
    open_cfw_easylogger_helpers_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_HELPERS_TAG_MAX + 1];
    open_cfw_easylogger_helpers_u8 tag_use_flag;
};

struct open_cfw_easylogger_helpers_filter {
    open_cfw_easylogger_helpers_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_HELPERS_TAG_MAX + 1];
    char keyword[OPEN_CFW_EASYLOGGER_HELPERS_KEYWORD_MAX + 1];
    struct open_cfw_easylogger_helpers_tag_level
        tag_level[OPEN_CFW_EASYLOGGER_HELPERS_TAG_LEVEL_COUNT];
};

struct open_cfw_easylogger_helpers_logger {
    struct open_cfw_easylogger_helpers_filter filter;
    open_cfw_easylogger_helpers_u32
        enabled_format_set[OPEN_CFW_EASYLOGGER_HELPERS_LEVEL_COUNT];
    open_cfw_easylogger_helpers_u8 init_ok;
    open_cfw_easylogger_helpers_u8 output_enabled;
    open_cfw_easylogger_helpers_u8 output_lock_enabled;
    open_cfw_easylogger_helpers_u8 output_is_locked_before_enable;
    open_cfw_easylogger_helpers_u8 output_is_locked_before_disable;
    open_cfw_easylogger_helpers_u8 text_color_enabled;
};

_Static_assert(
    sizeof(open_cfw_easylogger_helpers_u32) == 4U,
    "G2 EasyLogger size_t and format-set width changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_helpers_tag_level) == 0x21U,
    "G2 EasyLogger tag-level stride changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_helpers_tag_level,
        level
    ) == 0x00U,
    "G2 EasyLogger tag-level level offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_helpers_tag_level,
        tag
    ) == 0x01U,
    "G2 EasyLogger tag-level tag offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_helpers_tag_level,
        tag_use_flag
    ) == 0x20U,
    "G2 EasyLogger tag-level use flag offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_helpers_filter) == 0xD6U,
    "G2 EasyLogger filter layout changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_helpers_logger,
        enabled_format_set
    ) == 0xD8U,
    "G2 EasyLogger enabled-format table offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_helpers_logger,
        init_ok
    ) == 0xF0U,
    "G2 EasyLogger init flag offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_helpers_logger) == 0xF8U,
    "G2 EasyLogger object size changed"
);

/*
 * These seams deliberately use functions rather than an undefined data
 * symbol. The current isolated-leaf linker authenticates Thumb CALL/JUMP24
 * relocations; an external object would require MOVW/MOVT data relocations.
 */
#ifndef OPEN_CFW_EASYLOGGER_HELPERS_GET_LOGGER
struct open_cfw_easylogger_helpers_logger *
open_cfw_easylogger_helpers_get_logger(void);
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_LOGGER() \
    open_cfw_easylogger_helpers_get_logger()
#endif

#ifndef OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_FAILED
void open_cfw_easylogger_helpers_assert_failed(
    open_cfw_easylogger_helpers_u32 recovered_line
);
#define OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_FAILED(recovered_line) \
    open_cfw_easylogger_helpers_assert_failed((recovered_line))
#endif

open_cfw_easylogger_helpers_u32 open_cfw_easylogger_strcpy(
    open_cfw_easylogger_helpers_u32 current_length,
    char *destination,
    const char *source
);

open_cfw_easylogger_helpers_u8 open_cfw_easylogger_get_fmt_enabled(
    open_cfw_easylogger_helpers_u8 level,
    open_cfw_easylogger_helpers_u32 format_set
);

open_cfw_easylogger_helpers_u8
open_cfw_easylogger_get_fmt_used_and_enabled_u32(
    open_cfw_easylogger_helpers_u8 level,
    open_cfw_easylogger_helpers_u32 format_set,
    open_cfw_easylogger_helpers_u32 argument
);

open_cfw_easylogger_helpers_u8
open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
    open_cfw_easylogger_helpers_u8 level,
    open_cfw_easylogger_helpers_u32 format_set,
    const char *argument
);

#endif
