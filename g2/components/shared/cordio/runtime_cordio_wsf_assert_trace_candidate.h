/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room ABI for the G2 Cordio WSF assert and trace
 * functions.  The Ambiq files are proprietary source-family oracles only.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_WSF_ASSERT_TRACE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_WSF_ASSERT_TRACE_CANDIDATE_H

#include <stdarg.h>
#include <stdint.h>

enum {
    OPEN_CFW_CORDIO_WSF_TRACE_BUFFER_SIZE = 1024U,
    OPEN_CFW_CORDIO_WSF_ASSERT_LOG_LINE = 43U,
    OPEN_CFW_CORDIO_WSF_ASSERT_INTERNAL_LINE = 44U,
    OPEN_CFW_CORDIO_WSF_TRACE_ASSERT_LINE = 137U,
    OPEN_CFW_CORDIO_WSF_ASSERT_BACKEND_MASK = 0x04800000U
};

typedef void (*open_cfw_cordio_wsf_assert_hook_candidate_t)(
    const char *expression,
    const char *function,
    uint32_t line
);

extern open_cfw_cordio_wsf_assert_hook_candidate_t
    open_cfw_cordio_wsf_assert_hook_candidate;

uint32_t open_cfw_cordio_wsf_logger_flags_candidate(void);
void open_cfw_cordio_wsf_assert_structured_log_candidate(
    const char *file,
    uint16_t line
);
void open_cfw_cordio_wsf_assert_backend_log_candidate(
    uint32_t mask,
    const char *file,
    uint16_t line
);
void open_cfw_cordio_wsf_assert_internal_log_candidate(
    const char *expression,
    const char *function,
    uint32_t line
);
void open_cfw_cordio_wsf_assert_reset_candidate(void);

void open_cfw_cordio_wsf_trace_vsprintf_candidate(
    char *buffer,
    const char *format,
    va_list arguments
);
uint32_t open_cfw_cordio_wsf_trace_debug_printf_candidate(
    const char *format,
    ...
);

void open_cfw_cordio_wsf_assert_candidate(
    const char *file,
    uint16_t line
);
void open_cfw_cordio_wsf_trace_candidate(const char *format, ...);

#endif /* OPEN_CFW_RUNTIME_CORDIO_WSF_ASSERT_TRACE_CANDIDATE_H */
