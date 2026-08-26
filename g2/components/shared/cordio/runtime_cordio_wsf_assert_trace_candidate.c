/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-routed behavioral reconstruction of G2 WsfAssert/WsfTrace.
 * This deliberately preserves the stock unbounded formatting and double-
 * format debug path; callers must not treat it as a hardened logging API.
 */

#include "runtime_cordio_wsf_assert_trace_candidate.h"

#if !defined(OPEN_CFW_WSF_ASSERT_TRACE_ASSERT_ONLY) && \
    !defined(OPEN_CFW_WSF_ASSERT_TRACE_TRACE_ONLY)
#define OPEN_CFW_WSF_ASSERT_TRACE_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_WSF_ASSERT_TRACE_PRODUCTION
#define OPEN_CFW_WSF_ASSERT_FUNCTION ((const char *)0x0078C938U)
#define OPEN_CFW_WSF_ASSERT_EXPRESSION ((const char *)0x0078EE14U)
#define OPEN_CFW_WSF_ASSERT_PATH ((const char *)0x006DEFD4U)
#define OPEN_CFW_WSF_TRACE_PATH ((const char *)0x006DF094U)
#define OPEN_CFW_WSF_TRACE_NEWLINE ((const char *)0x0052A674U)
#define OPEN_CFW_WSF_ASSERT_HOOK \
    (*(open_cfw_cordio_wsf_assert_hook_candidate_t *)0x2007456CU)
#else
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
#define OPEN_CFW_WSF_ASSERT_FUNCTION \
    open_cfw_cordio_wsf_assert_function_candidate
#define OPEN_CFW_WSF_ASSERT_EXPRESSION \
    open_cfw_cordio_wsf_assert_expression_candidate
#define OPEN_CFW_WSF_ASSERT_PATH open_cfw_cordio_wsf_assert_path_candidate
#define OPEN_CFW_WSF_TRACE_PATH open_cfw_cordio_wsf_trace_path_candidate
#define OPEN_CFW_WSF_TRACE_NEWLINE "\n"
#define OPEN_CFW_WSF_ASSERT_HOOK open_cfw_cordio_wsf_assert_hook_candidate
#endif

#if defined(OPEN_CFW_WSF_ASSERT_TRACE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_ASSERT_TRACE_ASSERT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_assert_candidate(
    const char *file,
    uint16_t line
)
{
    volatile uint8_t escape = 0U;
#ifndef OPEN_CFW_WSF_ASSERT_TRACE_PRODUCTION
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
#else
    (void)line;
#endif

    if (file == (const char *)0) {
        if (OPEN_CFW_WSF_ASSERT_HOOK ==
            (open_cfw_cordio_wsf_assert_hook_candidate_t)0) {
#ifndef OPEN_CFW_WSF_ASSERT_TRACE_PRODUCTION
            open_cfw_cordio_wsf_assert_internal_log_candidate(
                OPEN_CFW_WSF_ASSERT_EXPRESSION,
                OPEN_CFW_WSF_ASSERT_FUNCTION,
                OPEN_CFW_CORDIO_WSF_ASSERT_INTERNAL_LINE
            );
#endif
            for (;;) {
                open_cfw_cordio_wsf_assert_reset_candidate();
            }
        }
        OPEN_CFW_WSF_ASSERT_HOOK(
            OPEN_CFW_WSF_ASSERT_EXPRESSION,
            OPEN_CFW_WSF_ASSERT_FUNCTION,
            OPEN_CFW_CORDIO_WSF_ASSERT_INTERNAL_LINE
        );
    }

    while (escape == 0U) {
        /* A debugger can write the volatile stack byte to permit return. */
    }

    (void)OPEN_CFW_WSF_ASSERT_PATH;
}
#endif

#if defined(OPEN_CFW_WSF_ASSERT_TRACE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_ASSERT_TRACE_TRACE_ONLY)
__attribute__((used, noinline))
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
            OPEN_CFW_WSF_TRACE_PATH,
            OPEN_CFW_CORDIO_WSF_TRACE_ASSERT_LINE
        );
    }
    (void)open_cfw_cordio_wsf_trace_debug_printf_candidate(
        OPEN_CFW_WSF_TRACE_NEWLINE
    );
}
#endif
