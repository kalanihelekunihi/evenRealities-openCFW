#include <stdint.h>

#define OPEN_CFW_FORMAT_APPEND_STREAM_FULL \
    ((const char *)(uintptr_t)0x11111111U)
#define OPEN_CFW_FORMAT_APPEND_IO_ERROR \
    ((const char *)(uintptr_t)0x22222222U)

#include "../../components/apollo_main/core_overlay/format_append.c"

struct open_cfw_format_output open_cfw_test_format_append_output;
unsigned int open_cfw_test_format_append_callback_result;
unsigned int open_cfw_test_format_append_callback_calls;
unsigned int open_cfw_test_format_append_callback_new_length;
void *open_cfw_test_format_append_callback_output;
const void *open_cfw_test_format_append_callback_data;
unsigned int open_cfw_test_format_append_callback_length;

unsigned int open_cfw_test_format_append_callback(
    struct open_cfw_format_output *output,
    const void *data,
    unsigned int length
)
{
    open_cfw_test_format_append_callback_calls += 1U;
    open_cfw_test_format_append_callback_output = output;
    open_cfw_test_format_append_callback_data = data;
    open_cfw_test_format_append_callback_length = length;
    if (open_cfw_test_format_append_callback_new_length != 0xFFFFFFFFU) {
        output->length = open_cfw_test_format_append_callback_new_length;
    }
    return open_cfw_test_format_append_callback_result;
}

void open_cfw_test_format_append_reset(void)
{
    open_cfw_test_format_append_output.write =
        (open_cfw_format_output_fn)0;
    open_cfw_test_format_append_output.context = (void *)0;
    open_cfw_test_format_append_output.capacity = 0U;
    open_cfw_test_format_append_output.length = 0U;
    open_cfw_test_format_append_output.error = (const char *)0;
    open_cfw_test_format_append_callback_result = 1U;
    open_cfw_test_format_append_callback_calls = 0U;
    open_cfw_test_format_append_callback_new_length = 0xFFFFFFFFU;
    open_cfw_test_format_append_callback_output = (void *)0;
    open_cfw_test_format_append_callback_data = (const void *)0;
    open_cfw_test_format_append_callback_length = 0U;
}

void *open_cfw_test_format_append_output_pointer(void)
{
    return &open_cfw_test_format_append_output;
}

void open_cfw_test_format_append_configure(
    unsigned int callback_enabled,
    unsigned int capacity,
    unsigned int length,
    uintptr_t error
)
{
    open_cfw_test_format_append_output.write =
        callback_enabled != 0U
            ? open_cfw_test_format_append_callback
            : (open_cfw_format_output_fn)0;
    open_cfw_test_format_append_output.capacity = capacity;
    open_cfw_test_format_append_output.length = length;
    open_cfw_test_format_append_output.error = (const char *)error;
}

unsigned int open_cfw_test_format_append_output_length(void)
{
    return open_cfw_test_format_append_output.length;
}

uintptr_t open_cfw_test_format_append_output_error(void)
{
    return (uintptr_t)open_cfw_test_format_append_output.error;
}
