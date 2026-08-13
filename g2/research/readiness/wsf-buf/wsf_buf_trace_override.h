#ifndef OPENCFW_WSF_BUF_TRACE_OVERRIDE_H
#define OPENCFW_WSF_BUF_TRACE_OVERRIDE_H

#include <stdint.h>

void open_cfw_wsf_buf_stock_warn1(
    uint32_t severity,
    const char *subsystem,
    const char *status,
    const char *message,
    uint32_t source_line,
    const char *source_file,
    uint32_t value
);

/* Suppress the proprietary archive header after defining the exact macros
 * needed by wsf_buf.c. Informational/allocation/free traces are compiled out
 * in stock. The retained allocation-failure metadata proves line 321. */
#define WSF_TRACE_H
#define WSF_TRACE_INFO1(message, value)
#define WSF_TRACE_INFO2(message, value1, value2)
#define WSF_TRACE_ALLOC2(message, value1, value2)
#define WSF_TRACE_FREE2(message, value1, value2)
#define WSF_TRACE_WARN1(message, value)                                      \
    open_cfw_wsf_buf_stock_warn1(                                           \
        1U, "WSF", "WARN", (message), 321U, __FILE__, (uint32_t)(value))

#endif
