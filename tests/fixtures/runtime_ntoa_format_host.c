/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter for the bounded mpaland/printf integer-format helper recovery.
 */

typedef void (*open_cfw_test_ntoa_callback)(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
);

static unsigned int open_cfw_test_ntoa_out_reverse(
    open_cfw_test_ntoa_callback output_callback,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    const char *reverse_buffer,
    unsigned int length,
    unsigned int width,
    unsigned int flags
);

#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE( \
    output_callback, \
    buffer, \
    index, \
    maximum_length, \
    reverse_buffer, \
    length, \
    width, \
    flags \
) \
    open_cfw_test_ntoa_out_reverse( \
        (output_callback), \
        (buffer), \
        (index), \
        (maximum_length), \
        (reverse_buffer), \
        (length), \
        (width), \
        (flags) \
    )

#include "../../components/apollo_main/core_overlay/runtime_ntoa_format.c"

#define OPEN_CFW_TEST_NTOA_GUARD_SIZE 4U
#define OPEN_CFW_TEST_NTOA_SCRATCH_SIZE 32U
#define OPEN_CFW_TEST_NTOA_OUTPUT_SIZE 128U

static unsigned char open_cfw_test_ntoa_scratch_bytes[
    OPEN_CFW_TEST_NTOA_GUARD_SIZE
    + OPEN_CFW_TEST_NTOA_SCRATCH_SIZE
    + OPEN_CFW_TEST_NTOA_GUARD_SIZE
];
static unsigned char
    open_cfw_test_ntoa_output[OPEN_CFW_TEST_NTOA_OUTPUT_SIZE];

unsigned int open_cfw_test_ntoa_reverse_calls;
unsigned int open_cfw_test_ntoa_callback_calls;
unsigned int open_cfw_test_ntoa_reverse_index;
unsigned int open_cfw_test_ntoa_reverse_maximum_length;
unsigned int open_cfw_test_ntoa_reverse_length;
unsigned int open_cfw_test_ntoa_reverse_width;
unsigned int open_cfw_test_ntoa_reverse_flags;

static void open_cfw_test_ntoa_emit(
    char character,
    void *buffer_value,
    unsigned int index,
    unsigned int maximum_length
)
{
    unsigned char *buffer = buffer_value;

    open_cfw_test_ntoa_callback_calls += 1U;
    if (index < maximum_length) {
        buffer[index] = (unsigned char)character;
    }
}

static unsigned int open_cfw_test_ntoa_out_reverse(
    open_cfw_test_ntoa_callback output_callback,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    const char *reverse_buffer,
    unsigned int length,
    unsigned int width,
    unsigned int flags
)
{
    unsigned int start_index = index;
    unsigned int reverse_length = length;

    open_cfw_test_ntoa_reverse_calls += 1U;
    open_cfw_test_ntoa_reverse_index = index;
    open_cfw_test_ntoa_reverse_maximum_length = maximum_length;
    open_cfw_test_ntoa_reverse_length = length;
    open_cfw_test_ntoa_reverse_width = width;
    open_cfw_test_ntoa_reverse_flags = flags;

    if ((flags & OPEN_CFW_RUNTIME_NTOA_LEFT) == 0U
        && (flags & OPEN_CFW_RUNTIME_NTOA_ZERO_PAD) == 0U) {
        unsigned int padding;

        for (padding = length; padding < width; padding += 1U) {
            output_callback(
                ' ',
                buffer,
                index,
                maximum_length
            );
            index += 1U;
        }
    }

    while (reverse_length != 0U) {
        reverse_length -= 1U;
        output_callback(
            reverse_buffer[reverse_length],
            buffer,
            index,
            maximum_length
        );
        index += 1U;
    }

    if ((flags & OPEN_CFW_RUNTIME_NTOA_LEFT) != 0U) {
        while (index - start_index < width) {
            output_callback(
                ' ',
                buffer,
                index,
                maximum_length
            );
            index += 1U;
        }
    }

    return index;
}

void open_cfw_test_ntoa_reset(void)
{
    unsigned int index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_ntoa_scratch_bytes);
        index += 1U
    ) {
        open_cfw_test_ntoa_scratch_bytes[index] = 0xa5U;
    }
    for (
        index = 0U;
        index < sizeof(open_cfw_test_ntoa_output);
        index += 1U
    ) {
        open_cfw_test_ntoa_output[index] = 0xccU;
    }

    open_cfw_test_ntoa_reverse_calls = 0U;
    open_cfw_test_ntoa_callback_calls = 0U;
    open_cfw_test_ntoa_reverse_index = 0U;
    open_cfw_test_ntoa_reverse_maximum_length = 0U;
    open_cfw_test_ntoa_reverse_length = 0U;
    open_cfw_test_ntoa_reverse_width = 0U;
    open_cfw_test_ntoa_reverse_flags = 0U;
}

unsigned int open_cfw_test_ntoa_execute(
    unsigned int index,
    unsigned int maximum_length,
    unsigned int length,
    unsigned int negative,
    unsigned int base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    return open_cfw_runtime_ntoa_format(
        open_cfw_test_ntoa_emit,
        open_cfw_test_ntoa_output,
        index,
        maximum_length,
        (char *)open_cfw_test_ntoa_scratch_bytes
            + OPEN_CFW_TEST_NTOA_GUARD_SIZE,
        length,
        (_Bool)negative,
        base,
        precision,
        width,
        flags
    );
}

unsigned char *open_cfw_test_ntoa_scratch(void)
{
    return open_cfw_test_ntoa_scratch_bytes
        + OPEN_CFW_TEST_NTOA_GUARD_SIZE;
}

unsigned char *open_cfw_test_ntoa_scratch_storage(void)
{
    return open_cfw_test_ntoa_scratch_bytes;
}

unsigned char *open_cfw_test_ntoa_output_bytes(void)
{
    return open_cfw_test_ntoa_output;
}
