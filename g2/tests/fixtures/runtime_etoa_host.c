/*
 * SPDX-License-Identifier: MIT
 *
 * Host call-boundary fixture for the source-owned mpaland _etoa.
 */

#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    unsigned int,
    unsigned int
);
#endif

static unsigned int open_cfw_test_runtime_etoa_ftoa(
    open_cfw_runtime_ntoa_output_fn,
    void *,
    unsigned int,
    unsigned int,
    double,
    unsigned int,
    unsigned int,
    unsigned int
);
static unsigned int open_cfw_test_runtime_etoa_ntoa_long(
    open_cfw_runtime_ntoa_output_fn,
    void *,
    unsigned int,
    unsigned int,
    unsigned int,
    _Bool,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);

#define OPEN_CFW_RUNTIME_ETOA_FTOA( \
    output, buffer, index, maximum_length, value, precision, width, flags \
) \
    open_cfw_test_runtime_etoa_ftoa( \
        (output), (buffer), (index), (maximum_length), \
        (value), (precision), (width), (flags) \
    )
#define OPEN_CFW_RUNTIME_ETOA_NTOA_LONG( \
    output, buffer, index, maximum_length, value, negative, base, \
    precision, width, flags \
) \
    open_cfw_test_runtime_etoa_ntoa_long( \
        (output), (buffer), (index), (maximum_length), (value), \
        (negative), (base), (precision), (width), (flags) \
    )

#include "../../components/apollo_main/core_overlay/runtime_etoa.c"

unsigned char open_cfw_test_runtime_etoa_buffer[32];
unsigned int open_cfw_test_runtime_etoa_ftoa_calls;
unsigned int open_cfw_test_runtime_etoa_ftoa_index;
unsigned int open_cfw_test_runtime_etoa_ftoa_maximum_length;
double open_cfw_test_runtime_etoa_ftoa_value;
unsigned int open_cfw_test_runtime_etoa_ftoa_precision;
unsigned int open_cfw_test_runtime_etoa_ftoa_width;
unsigned int open_cfw_test_runtime_etoa_ftoa_flags;
unsigned int open_cfw_test_runtime_etoa_ftoa_return;

unsigned int open_cfw_test_runtime_etoa_ntoa_calls;
unsigned int open_cfw_test_runtime_etoa_ntoa_index;
unsigned int open_cfw_test_runtime_etoa_ntoa_maximum_length;
unsigned int open_cfw_test_runtime_etoa_ntoa_value;
unsigned int open_cfw_test_runtime_etoa_ntoa_negative;
unsigned int open_cfw_test_runtime_etoa_ntoa_base;
unsigned int open_cfw_test_runtime_etoa_ntoa_precision;
unsigned int open_cfw_test_runtime_etoa_ntoa_width;
unsigned int open_cfw_test_runtime_etoa_ntoa_flags;
unsigned int open_cfw_test_runtime_etoa_ntoa_return;

unsigned int open_cfw_test_runtime_etoa_output_calls;
unsigned char open_cfw_test_runtime_etoa_output_character[64];
unsigned int open_cfw_test_runtime_etoa_output_index[64];
unsigned int open_cfw_test_runtime_etoa_output_maximum_length[64];

static void open_cfw_test_runtime_etoa_output(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    unsigned int event = open_cfw_test_runtime_etoa_output_calls;

    (void)buffer;
    if (event < 64U) {
        open_cfw_test_runtime_etoa_output_character[event] =
            (unsigned char)character;
        open_cfw_test_runtime_etoa_output_index[event] = index;
        open_cfw_test_runtime_etoa_output_maximum_length[event] =
            maximum_length;
    }
    open_cfw_test_runtime_etoa_output_calls = event + 1U;
}

static unsigned int open_cfw_test_runtime_etoa_ftoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    double value,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    (void)output;
    (void)buffer;
    open_cfw_test_runtime_etoa_ftoa_calls += 1U;
    open_cfw_test_runtime_etoa_ftoa_index = index;
    open_cfw_test_runtime_etoa_ftoa_maximum_length = maximum_length;
    open_cfw_test_runtime_etoa_ftoa_value = value;
    open_cfw_test_runtime_etoa_ftoa_precision = precision;
    open_cfw_test_runtime_etoa_ftoa_width = width;
    open_cfw_test_runtime_etoa_ftoa_flags = flags;
    return open_cfw_test_runtime_etoa_ftoa_return;
}

static unsigned int open_cfw_test_runtime_etoa_ntoa_long(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    unsigned int value,
    _Bool negative,
    unsigned int base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    (void)output;
    (void)buffer;
    open_cfw_test_runtime_etoa_ntoa_calls += 1U;
    open_cfw_test_runtime_etoa_ntoa_index = index;
    open_cfw_test_runtime_etoa_ntoa_maximum_length = maximum_length;
    open_cfw_test_runtime_etoa_ntoa_value = value;
    open_cfw_test_runtime_etoa_ntoa_negative = negative ? 1U : 0U;
    open_cfw_test_runtime_etoa_ntoa_base = base;
    open_cfw_test_runtime_etoa_ntoa_precision = precision;
    open_cfw_test_runtime_etoa_ntoa_width = width;
    open_cfw_test_runtime_etoa_ntoa_flags = flags;
    return open_cfw_test_runtime_etoa_ntoa_return;
}

void open_cfw_test_runtime_etoa_reset(
    unsigned int ftoa_return,
    unsigned int ntoa_return
)
{
    unsigned int index;

    for (index = 0U; index < 32U; index += 1U) {
        open_cfw_test_runtime_etoa_buffer[index] = 0xC3U;
    }
    for (index = 0U; index < 64U; index += 1U) {
        open_cfw_test_runtime_etoa_output_character[index] = 0U;
        open_cfw_test_runtime_etoa_output_index[index] = 0U;
        open_cfw_test_runtime_etoa_output_maximum_length[index] = 0U;
    }
    open_cfw_test_runtime_etoa_ftoa_calls = 0U;
    open_cfw_test_runtime_etoa_ftoa_index = 0U;
    open_cfw_test_runtime_etoa_ftoa_maximum_length = 0U;
    open_cfw_test_runtime_etoa_ftoa_value = 0.0;
    open_cfw_test_runtime_etoa_ftoa_precision = 0U;
    open_cfw_test_runtime_etoa_ftoa_width = 0U;
    open_cfw_test_runtime_etoa_ftoa_flags = 0U;
    open_cfw_test_runtime_etoa_ftoa_return = ftoa_return;
    open_cfw_test_runtime_etoa_ntoa_calls = 0U;
    open_cfw_test_runtime_etoa_ntoa_index = 0U;
    open_cfw_test_runtime_etoa_ntoa_maximum_length = 0U;
    open_cfw_test_runtime_etoa_ntoa_value = 0U;
    open_cfw_test_runtime_etoa_ntoa_negative = 0U;
    open_cfw_test_runtime_etoa_ntoa_base = 0U;
    open_cfw_test_runtime_etoa_ntoa_precision = 0U;
    open_cfw_test_runtime_etoa_ntoa_width = 0U;
    open_cfw_test_runtime_etoa_ntoa_flags = 0U;
    open_cfw_test_runtime_etoa_ntoa_return = ntoa_return;
    open_cfw_test_runtime_etoa_output_calls = 0U;
}

unsigned int open_cfw_test_runtime_etoa_execute(
    double value,
    unsigned int precision,
    unsigned int width,
    unsigned int flags,
    unsigned int index,
    unsigned int maximum_length
)
{
    return open_cfw_runtime_etoa(
        open_cfw_test_runtime_etoa_output,
        open_cfw_test_runtime_etoa_buffer,
        index,
        maximum_length,
        value,
        precision,
        width,
        flags
    );
}
