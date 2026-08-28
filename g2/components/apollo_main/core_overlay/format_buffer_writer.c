/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 length-prefixed formatting span
 * writer at 0x00490DB6. Its exact boundary, callers, and retained dependency
 * ABIs are recorded in EVIDENCE.md.
 */

unsigned int open_cfw_format_u64_prefix_write(
    void *output,
    unsigned long long value
);
unsigned int open_cfw_format_append(
    void *output,
    const void *data,
    unsigned int length
);

#ifndef OPEN_CFW_FORMAT_BUFFER_PREFIX
#define OPEN_CFW_FORMAT_BUFFER_PREFIX(output, length) \
    (open_cfw_format_u64_prefix_write( \
        (output), \
        (unsigned long long)(length) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_BUFFER_APPEND
#define OPEN_CFW_FORMAT_BUFFER_APPEND(output, data, length) \
    (open_cfw_format_append( \
        (output), \
        (data), \
        (length) \
    ))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_buffer_write(
    void *output,
    const void *data,
    unsigned int length
)
{
    if (OPEN_CFW_FORMAT_BUFFER_PREFIX(output, length) == 0U) {
        return 0U;
    }
    return OPEN_CFW_FORMAT_BUFFER_APPEND(output, data, length);
}
