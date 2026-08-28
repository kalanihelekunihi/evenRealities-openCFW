/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 shared formatting append primitive
 * at 0x00490616. Its exact object layout, boundary, callers, and error
 * literals are recorded in EVIDENCE.md.
 */

struct open_cfw_format_output;

typedef unsigned int (*open_cfw_format_output_fn)(
    struct open_cfw_format_output *output,
    const void *data,
    unsigned int length
);

struct open_cfw_format_output {
    open_cfw_format_output_fn write;
    void *context;
    unsigned int capacity;
    unsigned int length;
    const char *error;
};

#ifndef OPEN_CFW_FORMAT_APPEND_STREAM_FULL
#define OPEN_CFW_FORMAT_APPEND_STREAM_FULL \
    ((const char *)0x0078B6A8U)
#endif

#ifndef OPEN_CFW_FORMAT_APPEND_IO_ERROR
#define OPEN_CFW_FORMAT_APPEND_IO_ERROR \
    ((const char *)0x0078B6B4U)
#endif

static void open_cfw_format_append_error(
    struct open_cfw_format_output *output,
    const char *fallback
)
{
    if (output->error == (const char *)0) {
        output->error = fallback;
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_format_append(
    void *raw_output,
    const void *data,
    unsigned int length
)
{
    struct open_cfw_format_output *output =
        (struct open_cfw_format_output *)raw_output;

    if ((length != 0U) && (output->write != (open_cfw_format_output_fn)0)) {
        const unsigned int next = output->length + length;

        if ((next < output->length) || (output->capacity < next)) {
            open_cfw_format_append_error(
                output,
                OPEN_CFW_FORMAT_APPEND_STREAM_FULL
            );
            return 0U;
        }
        if (output->write(output, data, length) == 0U) {
            open_cfw_format_append_error(
                output,
                OPEN_CFW_FORMAT_APPEND_IO_ERROR
            );
            return 0U;
        }
    }

    output->length += length;
    return 1U;
}
