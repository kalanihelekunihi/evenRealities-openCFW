#include <stdint.h>

typedef unsigned int (*open_cfw_format_extension_encode_fn)(
    void *output,
    const void *field_descriptor,
    const void *argument
);

unsigned int open_cfw_test_format_complex_prefix_result;
unsigned int open_cfw_test_format_complex_append_result;
unsigned int open_cfw_test_format_complex_buffer_result;
unsigned int open_cfw_test_format_complex_extension_result;
unsigned int open_cfw_test_format_complex_encode_result[2];
unsigned int open_cfw_test_format_complex_encode_bytes[2];
unsigned int open_cfw_test_format_complex_encode_state[2];
unsigned int open_cfw_test_format_complex_encode_error[2];
unsigned int open_cfw_test_format_complex_encode_calls;
unsigned int open_cfw_test_format_complex_prefix_calls;
unsigned int open_cfw_test_format_complex_append_calls;
unsigned int open_cfw_test_format_complex_buffer_calls;
unsigned int open_cfw_test_format_complex_extension_calls;
unsigned int open_cfw_test_format_complex_error_calls;
unsigned int open_cfw_test_format_complex_prefix_length;
unsigned int open_cfw_test_format_complex_append_length;
unsigned int open_cfw_test_format_complex_buffer_length;
unsigned int open_cfw_test_format_complex_last_error;
unsigned int open_cfw_test_format_complex_stream_before[2][5];
void *open_cfw_test_format_complex_encode_output[2];
const void *open_cfw_test_format_complex_encode_descriptor[2];
const void *open_cfw_test_format_complex_encode_source[2];
void *open_cfw_test_format_complex_prefix_output;
void *open_cfw_test_format_complex_append_output;
const void *open_cfw_test_format_complex_append_data;
void *open_cfw_test_format_complex_buffer_output;
const void *open_cfw_test_format_complex_buffer_data;
void *open_cfw_test_format_complex_extension_output;
const void *open_cfw_test_format_complex_extension_descriptor;
const void *open_cfw_test_format_complex_extension_argument;
const void *open_cfw_test_format_complex_data;
const unsigned char *open_cfw_test_format_complex_extension;
const void *open_cfw_test_format_complex_submessage;
unsigned char open_cfw_test_format_complex_extension_record[16];
unsigned int open_cfw_test_format_complex_extension_enabled;

static unsigned int open_cfw_test_format_complex_word(
    const void *object,
    unsigned int offset
)
{
    return *(const unsigned int *)(const void *)(
        (const unsigned char *)object + offset
    );
}

static void open_cfw_test_format_complex_set_word(
    void *object,
    unsigned int offset,
    unsigned int value
)
{
    *(unsigned int *)(void *)(
        (unsigned char *)object + offset
    ) = value;
}

void open_cfw_test_format_complex_reset(void)
{
    unsigned int index;
    unsigned int field;

    open_cfw_test_format_complex_prefix_result = 1U;
    open_cfw_test_format_complex_append_result = 1U;
    open_cfw_test_format_complex_buffer_result = 1U;
    open_cfw_test_format_complex_extension_result = 1U;
    open_cfw_test_format_complex_encode_calls = 0U;
    open_cfw_test_format_complex_prefix_calls = 0U;
    open_cfw_test_format_complex_append_calls = 0U;
    open_cfw_test_format_complex_buffer_calls = 0U;
    open_cfw_test_format_complex_extension_calls = 0U;
    open_cfw_test_format_complex_error_calls = 0U;
    open_cfw_test_format_complex_prefix_length = 0U;
    open_cfw_test_format_complex_append_length = 0U;
    open_cfw_test_format_complex_buffer_length = 0U;
    open_cfw_test_format_complex_last_error = 0U;
    open_cfw_test_format_complex_prefix_output = (void *)0;
    open_cfw_test_format_complex_append_output = (void *)0;
    open_cfw_test_format_complex_append_data = (const void *)0;
    open_cfw_test_format_complex_buffer_output = (void *)0;
    open_cfw_test_format_complex_buffer_data = (const void *)0;
    open_cfw_test_format_complex_extension_output = (void *)0;
    open_cfw_test_format_complex_extension_descriptor = (const void *)0;
    open_cfw_test_format_complex_extension_argument = (const void *)0;
    open_cfw_test_format_complex_data = (const void *)0;
    open_cfw_test_format_complex_extension = (const unsigned char *)0;
    open_cfw_test_format_complex_submessage = (const void *)0;
    open_cfw_test_format_complex_extension_enabled = 0U;
    for (index = 0U; index < 2U; index += 1U) {
        open_cfw_test_format_complex_encode_result[index] = 1U;
        open_cfw_test_format_complex_encode_bytes[index] = 0U;
        open_cfw_test_format_complex_encode_state[index] = 0U;
        open_cfw_test_format_complex_encode_error[index] = 0U;
        open_cfw_test_format_complex_encode_output[index] = (void *)0;
        open_cfw_test_format_complex_encode_descriptor[index] =
            (const void *)0;
        open_cfw_test_format_complex_encode_source[index] =
            (const void *)0;
        for (field = 0U; field < 5U; field += 1U) {
            open_cfw_test_format_complex_stream_before[index][field] = 0U;
        }
    }
    for (index = 0U; index < 16U; index += 1U) {
        open_cfw_test_format_complex_extension_record[index] = 0U;
    }
}

unsigned int open_cfw_test_format_complex_encode(
    void *output,
    const void *descriptor,
    const void *source
)
{
    unsigned int index = open_cfw_test_format_complex_encode_calls;
    unsigned int field;

    if (index > 1U) {
        index = 1U;
    }
    open_cfw_test_format_complex_encode_calls += 1U;
    open_cfw_test_format_complex_encode_output[index] = output;
    open_cfw_test_format_complex_encode_descriptor[index] = descriptor;
    open_cfw_test_format_complex_encode_source[index] = source;
    for (field = 0U; field < 5U; field += 1U) {
        open_cfw_test_format_complex_stream_before[index][field] =
            open_cfw_test_format_complex_word(output, field * 4U);
    }
    open_cfw_test_format_complex_set_word(
        output,
        0x04U,
        open_cfw_test_format_complex_encode_state[index]
    );
    open_cfw_test_format_complex_set_word(
        output,
        0x0CU,
        open_cfw_test_format_complex_encode_bytes[index]
    );
    open_cfw_test_format_complex_set_word(
        output,
        0x10U,
        open_cfw_test_format_complex_encode_error[index]
    );
    return open_cfw_test_format_complex_encode_result[index];
}

unsigned int open_cfw_test_format_complex_prefix(
    void *output,
    unsigned long long length
)
{
    open_cfw_test_format_complex_prefix_calls += 1U;
    open_cfw_test_format_complex_prefix_output = output;
    open_cfw_test_format_complex_prefix_length = (unsigned int)length;
    return open_cfw_test_format_complex_prefix_result;
}

unsigned int open_cfw_test_format_complex_append(
    void *output,
    const void *data,
    unsigned int length
)
{
    open_cfw_test_format_complex_append_calls += 1U;
    open_cfw_test_format_complex_append_output = output;
    open_cfw_test_format_complex_append_data = data;
    open_cfw_test_format_complex_append_length = length;
    return open_cfw_test_format_complex_append_result;
}

unsigned int open_cfw_test_format_complex_buffer(
    void *output,
    const void *data,
    unsigned int length
)
{
    open_cfw_test_format_complex_buffer_calls += 1U;
    open_cfw_test_format_complex_buffer_output = output;
    open_cfw_test_format_complex_buffer_data = data;
    open_cfw_test_format_complex_buffer_length = length;
    return open_cfw_test_format_complex_buffer_result;
}

void open_cfw_test_format_complex_set_error(
    void *output,
    unsigned int error
)
{
    unsigned int current =
        open_cfw_test_format_complex_word(output, 0x10U);

    open_cfw_test_format_complex_error_calls += 1U;
    open_cfw_test_format_complex_last_error = error;
    if (current == 0U) {
        open_cfw_test_format_complex_set_word(output, 0x10U, error);
    }
}

unsigned int open_cfw_test_format_complex_extension_callback(
    void *output,
    const void *descriptor,
    const void *argument
)
{
    (void)output;
    (void)descriptor;
    (void)argument;
    return 1U;
}

open_cfw_format_extension_encode_fn
open_cfw_test_format_complex_read_extension_callback(const void *record)
{
    (void)record;
    if (open_cfw_test_format_complex_extension_enabled == 0U) {
        return (open_cfw_format_extension_encode_fn)0;
    }
    return open_cfw_test_format_complex_extension_callback;
}

unsigned int open_cfw_test_format_complex_call_extension(
    open_cfw_format_extension_encode_fn callback,
    void *output,
    const void *descriptor,
    const void *argument
)
{
    open_cfw_test_format_complex_extension_calls += 1U;
    open_cfw_test_format_complex_extension_output = output;
    open_cfw_test_format_complex_extension_descriptor = descriptor;
    open_cfw_test_format_complex_extension_argument = argument;
    (void)callback;
    return open_cfw_test_format_complex_extension_result;
}

#define OPEN_CFW_FORMAT_COMPLEX_MESSAGE_ENCODE(output, descriptor, source) \
    open_cfw_test_format_complex_encode((output), (descriptor), (source))
#define OPEN_CFW_FORMAT_COMPLEX_PREFIX(output, length) \
    open_cfw_test_format_complex_prefix((output), (length))
#define OPEN_CFW_FORMAT_COMPLEX_APPEND(output, data, length) \
    open_cfw_test_format_complex_append((output), (data), (length))
#define OPEN_CFW_FORMAT_COMPLEX_BUFFER(output, data, length) \
    open_cfw_test_format_complex_buffer((output), (data), (length))
#define OPEN_CFW_FORMAT_COMPLEX_DATA(descriptor) \
    (open_cfw_test_format_complex_data)
#define OPEN_CFW_FORMAT_COMPLEX_EXTENSION(descriptor) \
    (open_cfw_test_format_complex_extension)
#define OPEN_CFW_FORMAT_COMPLEX_SUBMESSAGE(descriptor) \
    (open_cfw_test_format_complex_submessage)
#define OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALLBACK(record) \
    open_cfw_test_format_complex_read_extension_callback((record))
#define OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALL( \
    callback, \
    output, \
    descriptor, \
    argument \
) \
    open_cfw_test_format_complex_call_extension( \
        (callback), \
        (output), \
        (descriptor), \
        (argument) \
    )
#define OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, error) \
    open_cfw_test_format_complex_set_error((output), (error))

#include "../../components/apollo_main/core_overlay/format_complex.c"
