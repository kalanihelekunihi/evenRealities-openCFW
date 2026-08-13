/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded behavioral reconstruction of G2 WsfAssert/WsfTrace.
 * This deliberately preserves the stock unbounded formatting and double-
 * format debug path; callers must not treat it as a hardened logging API.
 */

#include "runtime_cordio_wsf_assert_trace_candidate.h"

static const char open_cfw_cordio_wsf_assert_function_candidate[] =
    "WsfAssert";
static const char open_cfw_cordio_wsf_assert_expression_candidate[] =
    "pFile";
static const char open_cfw_cordio_wsf_assert_path_candidate[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\wsf\\"
    "sources\\port\\freertos\\wsf_assert.c";
static const char open_cfw_cordio_wsf_trace_path_candidate[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\wsf\\"
    "sources\\port\\freertos\\wsf_trace.c";

void open_cfw_cordio_wsf_assert_candidate(
    const char *file,
    uint16_t line
)
{
    volatile uint8_t escape = 0U;
    uint32_t flags;

    flags = open_cfw_cordio_wsf_logger_flags_candidate();
    if ((flags & 0x02U) != 0U) {
        open_cfw_cordio_wsf_assert_structured_log_candidate(file, line);
    }

    flags = open_cfw_cordio_wsf_logger_flags_candidate();
    if (((flags & 0x01U) != 0U)
        || ((open_cfw_cordio_wsf_logger_flags_candidate() & 0x04U) != 0U)) {
        open_cfw_cordio_wsf_assert_backend_log_candidate(
            OPEN_CFW_CORDIO_WSF_ASSERT_BACKEND_MASK,
            file,
            line
        );
    }

    if (file == (const char *)0) {
        if (open_cfw_cordio_wsf_assert_hook_candidate ==
            (open_cfw_cordio_wsf_assert_hook_candidate_t)0) {
            open_cfw_cordio_wsf_assert_internal_log_candidate(
                open_cfw_cordio_wsf_assert_expression_candidate,
                open_cfw_cordio_wsf_assert_function_candidate,
                OPEN_CFW_CORDIO_WSF_ASSERT_INTERNAL_LINE
            );
            for (;;) {
                open_cfw_cordio_wsf_assert_reset_candidate();
            }
        }
        open_cfw_cordio_wsf_assert_hook_candidate(
            open_cfw_cordio_wsf_assert_expression_candidate,
            open_cfw_cordio_wsf_assert_function_candidate,
            OPEN_CFW_CORDIO_WSF_ASSERT_INTERNAL_LINE
        );
    }

    while (escape == 0U) {
        /* A debugger can write the volatile stack byte to permit return. */
    }

    (void)open_cfw_cordio_wsf_assert_path_candidate;
}

void open_cfw_cordio_wsf_trace_candidate(const char *format, ...)
{
    char buffer[OPEN_CFW_CORDIO_WSF_TRACE_BUFFER_SIZE];
    uint32_t characters;
    va_list arguments;

    va_start(arguments, format);
    open_cfw_cordio_wsf_trace_vsprintf_candidate(buffer, format, arguments);
    va_end(arguments);

    characters = open_cfw_cordio_wsf_trace_debug_printf_candidate(buffer);
    if (characters >= OPEN_CFW_CORDIO_WSF_TRACE_BUFFER_SIZE) {
        open_cfw_cordio_wsf_assert_candidate(
            open_cfw_cordio_wsf_trace_path_candidate,
            OPEN_CFW_CORDIO_WSF_TRACE_ASSERT_LINE
        );
    }
    (void)open_cfw_cordio_wsf_trace_debug_printf_candidate("\n");
}
