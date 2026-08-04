/*
 * SPDX-License-Identifier: MIT
 *
 * Even Realities G2 image seams for the source-owned EasyLogger helper
 * quartet.  The helper algorithms are shared by Apollo main and the S200
 * bootloader; this file binds the two image-specific logger objects and the
 * released assertion policy recovered by focused disassembly.
 *
 * Assertion text continues to use authenticated strings in the official
 * image.  The logger output and fail-stop wait functions also remain explicit
 * binary seams.  Moving those larger functions and their diagnostic strings
 * to source is a later, independently reviewable boundary.
 */

#include "runtime_easylogger_helpers.h"

typedef void (*open_cfw_easylogger_helpers_assert_hook_fn)(
    const char *expression,
    const char *function,
    open_cfw_easylogger_helpers_u32 line
);

typedef void (*open_cfw_easylogger_helpers_output_fn)(
    open_cfw_easylogger_helpers_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...
);

typedef void (*open_cfw_easylogger_helpers_wait_fn)(void);

#if \
    OPEN_CFW_EASYLOGGER_HELPERS_PROFILE == \
        OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_APOLLO_MAIN
#define OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_HOOK_ADDRESS 0x2007456CU
#define OPEN_CFW_EASYLOGGER_HELPERS_OUTPUT_THUMB_ADDRESS 0x0043D575U
#define OPEN_CFW_EASYLOGGER_HELPERS_WAIT_THUMB_ADDRESS 0x0044B0AFU
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_EXPRESSION_ADDRESS 0x0076B634U
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FUNCTION_ADDRESS 0x00785DC0U
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FILE_ADDRESS 0x006E3098U
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FORMAT_ADDRESS 0x007542A8U
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_TAG_ADDRESS 0x0078D4ECU
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_DST_EXPRESSION_ADDRESS 0x0044B70CU
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_SRC_EXPRESSION_ADDRESS 0x0044B710U
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FUNCTION_ADDRESS 0x0078A9ACU
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FILE_ADDRESS 0x006DD234U
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FORMAT_ADDRESS 0x00754314U
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_TAG_ADDRESS 0x0078D51CU
#elif \
    OPEN_CFW_EASYLOGGER_HELPERS_PROFILE == \
        OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER
#define OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_HOOK_ADDRESS 0x200270E4U
#define OPEN_CFW_EASYLOGGER_HELPERS_OUTPUT_THUMB_ADDRESS 0x004176CFU
#define OPEN_CFW_EASYLOGGER_HELPERS_WAIT_THUMB_ADDRESS 0x0041AC8BU
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_EXPRESSION_ADDRESS 0x004335CCU
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FUNCTION_ADDRESS 0x00433D18U
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FILE_ADDRESS 0x00430EC0U
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FORMAT_ADDRESS 0x00432E98U
#define OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_TAG_ADDRESS 0x0043406CU
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_DST_EXPRESSION_ADDRESS 0x0041B1FCU
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_SRC_EXPRESSION_ADDRESS 0x0041B200U
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FUNCTION_ADDRESS 0x00433F5CU
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FILE_ADDRESS 0x00430DA0U
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FORMAT_ADDRESS 0x00432EBCU
#define OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_TAG_ADDRESS 0x0043408CU
#else
#error "unsupported G2 EasyLogger helper seam profile"
#endif

#if defined(OPEN_CFW_EASYLOGGER_HELPER_SEAMS_BUILD_LEAF) && \
    (defined(OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_GET_LOGGER) + \
        defined(OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_ASSERT_FAILED)) != 1
#error "select exactly one EasyLogger helper seam leaf"
#endif

#if !defined(OPEN_CFW_EASYLOGGER_HELPER_SEAMS_BUILD_LEAF) || \
    defined(OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_GET_LOGGER)
__attribute__((used, noinline))
struct open_cfw_easylogger_helpers_logger *
open_cfw_easylogger_helpers_get_logger(void)
{
    return (struct open_cfw_easylogger_helpers_logger *)
        (open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS;
}
#endif

#if !defined(OPEN_CFW_EASYLOGGER_HELPER_SEAMS_BUILD_LEAF) || \
    defined(OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_ASSERT_FAILED)
__attribute__((used, noinline))
void open_cfw_easylogger_helpers_assert_failed(
    open_cfw_easylogger_helpers_u32 recovered_line
)
{
    const char *expression;
    const char *function;
    const char *file;
    const char *format;
    const char *tag;
    open_cfw_easylogger_helpers_assert_hook_fn hook;

    if (
        recovered_line ==
            OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_GET_FMT_LINE
    ) {
        expression = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_EXPRESSION_ADDRESS;
        function = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FUNCTION_ADDRESS;
        file = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FILE_ADDRESS;
        format = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_FORMAT_ADDRESS;
        tag = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_GET_FMT_TAG_ADDRESS;
    } else {
        expression = (const char *)(open_cfw_easylogger_helpers_uintptr)(
            recovered_line ==
                    OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_DST_LINE
                ? OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_DST_EXPRESSION_ADDRESS
                : OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_SRC_EXPRESSION_ADDRESS
        );
        function = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FUNCTION_ADDRESS;
        file = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FILE_ADDRESS;
        format = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_FORMAT_ADDRESS;
        tag = (const char *)(open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_TAG_ADDRESS;
    }

    hook = *(open_cfw_easylogger_helpers_assert_hook_fn volatile *)
        (open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_HOOK_ADDRESS;
    if (hook != (open_cfw_easylogger_helpers_assert_hook_fn)0) {
        hook(expression, function, recovered_line);
        return;
    }

    ((open_cfw_easylogger_helpers_output_fn)
        (open_cfw_easylogger_helpers_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_OUTPUT_THUMB_ADDRESS)(
                0U,
                tag,
                file,
                function,
                (long)recovered_line,
                format,
                expression,
                function,
                (long)recovered_line
            );
    for (;;) {
        ((open_cfw_easylogger_helpers_wait_fn)
            (open_cfw_easylogger_helpers_uintptr)
                OPEN_CFW_EASYLOGGER_HELPERS_WAIT_THUMB_ADDRESS)();
    }
}
#endif
