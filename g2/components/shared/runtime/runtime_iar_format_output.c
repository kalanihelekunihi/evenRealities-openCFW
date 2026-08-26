/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room IAR DLIB printf-core ABI adapter. The stock wrappers own their
 * buffer/stream states and final termination; this adapter supplies only the
 * formatter engine and calls the wrapper-selected two-argument writer.
 */

#include "runtime_iar_format_output.h"

typedef void (*open_cfw_runtime_format_output_fn)(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
);

extern int open_cfw_runtime_iar_vsnprintf_engine(
    open_cfw_runtime_format_output_fn output,
    unsigned char *buffer,
    unsigned int maximum_length,
    const unsigned char *format,
    va_list arguments
);

struct open_cfw_runtime_iar_format_context {
    open_cfw_runtime_iar_format_writer_fn writer;
    void *state;
    unsigned int pending;
    unsigned int have_pending;
    unsigned int failed;
};

/*
 * The maintained formatter emits one final NUL for buffer APIs. DLIB's core
 * does not send that terminator to its writer: each stock wrapper terminates
 * its own destination. Keeping one character pending makes the final callback
 * flush the last real character while leaving the synthetic NUL suppressed;
 * an actual `%c` NUL is still flushed when the synthetic NUL arrives.
 */
__attribute__((used, noinline))
void open_cfw_runtime_iar_format_bridge(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    struct open_cfw_runtime_iar_format_context *context =
        (struct open_cfw_runtime_iar_format_context *)buffer;

    (void)index;
    (void)maximum_length;
    if (context->have_pending != 0U && context->failed == 0U) {
        void *next = context->writer(context->state, context->pending);

        if (next == (void *)0) {
            context->failed = 1U;
        }
        else {
            context->state = next;
        }
    }
    context->pending = (unsigned char)character;
    context->have_pending = 1U;
}

__attribute__((used, noinline))
int open_cfw_runtime_iar_vformat(
    open_cfw_runtime_iar_format_writer_fn writer,
    void *state,
    const unsigned char *format,
    va_list arguments,
    int secure
)
{
    struct open_cfw_runtime_iar_format_context context;
    int result;

    /* No stock wrapper passes a nonzero secure flag. Fail closed if a future
     * route tries to claim unimplemented Annex-K behavior. */
    if (secure != 0 || writer == (open_cfw_runtime_iar_format_writer_fn)0
        || format == (const unsigned char *)0) {
        return -1;
    }
    context.writer = writer;
    context.state = state;
    context.pending = 0U;
    context.have_pending = 0U;
    context.failed = 0U;
    result = open_cfw_runtime_iar_vsnprintf_engine(
        open_cfw_runtime_iar_format_bridge,
        (unsigned char *)&context,
        0xFFFFFFFFU,
        format,
        arguments
    );
    return context.failed != 0U ? -1 : result;
}

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, noinline, pcs("aapcs")))
int open_cfw_runtime_iar_printf_core(
    open_cfw_runtime_iar_format_writer_fn writer,
    void *state,
    const unsigned char *format,
    void **argument_cursor,
    int secure
)
{
    __builtin_va_list arguments;

    arguments.__ap = *argument_cursor;
    return open_cfw_runtime_iar_vformat(
        writer, state, format, arguments, secure
    );
}
#endif
