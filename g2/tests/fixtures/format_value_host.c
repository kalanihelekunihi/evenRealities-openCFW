#include <stdint.h>

unsigned int open_cfw_test_format_value_type;
unsigned int open_cfw_test_format_value_key_result;
unsigned int open_cfw_test_format_value_adapter_result;
unsigned int open_cfw_test_format_value_key_calls;
unsigned int open_cfw_test_format_value_adapter_calls;
unsigned int open_cfw_test_format_value_adapter_kind;
unsigned int open_cfw_test_format_value_error_calls;
unsigned int open_cfw_test_format_value_last_error;
const void *open_cfw_test_format_value_data;
void *open_cfw_test_format_value_last_output;
const void *open_cfw_test_format_value_last_descriptor;

void open_cfw_test_format_value_reset(void)
{
    open_cfw_test_format_value_type = 0U;
    open_cfw_test_format_value_key_result = 1U;
    open_cfw_test_format_value_adapter_result = 1U;
    open_cfw_test_format_value_key_calls = 0U;
    open_cfw_test_format_value_adapter_calls = 0U;
    open_cfw_test_format_value_adapter_kind = 0U;
    open_cfw_test_format_value_error_calls = 0U;
    open_cfw_test_format_value_last_error = 0U;
    open_cfw_test_format_value_data = (const void *)0x11112222U;
    open_cfw_test_format_value_last_output = (void *)0;
    open_cfw_test_format_value_last_descriptor = (const void *)0;
}

static unsigned int open_cfw_test_format_value_adapter(
    void *output,
    const void *descriptor,
    unsigned int kind
)
{
    open_cfw_test_format_value_adapter_calls += 1U;
    open_cfw_test_format_value_adapter_kind = kind;
    open_cfw_test_format_value_last_output = output;
    open_cfw_test_format_value_last_descriptor = descriptor;
    return open_cfw_test_format_value_adapter_result;
}

unsigned int open_cfw_format_descriptor_key_write(
    void *output,
    const void *descriptor
)
{
    open_cfw_test_format_value_key_calls += 1U;
    open_cfw_test_format_value_last_output = output;
    open_cfw_test_format_value_last_descriptor = descriptor;
    return open_cfw_test_format_value_key_result;
}

unsigned int open_cfw_format_bool_write(
    void *output,
    const void *descriptor
)
{
    return open_cfw_test_format_value_adapter(output, descriptor, 1U);
}

unsigned int open_cfw_format_integer_write(
    void *output,
    const void *descriptor
)
{
    return open_cfw_test_format_value_adapter(output, descriptor, 2U);
}

unsigned int open_cfw_format_fixed_write(
    void *output,
    const void *descriptor
)
{
    return open_cfw_test_format_value_adapter(output, descriptor, 3U);
}

unsigned int open_cfw_format_bytes_write(
    void *output,
    const void *descriptor
)
{
    return open_cfw_test_format_value_adapter(output, descriptor, 4U);
}

unsigned int open_cfw_format_string_write(
    void *output,
    const void *descriptor
)
{
    return open_cfw_test_format_value_adapter(output, descriptor, 5U);
}

unsigned int open_cfw_format_submessage_field_write(
    void *output,
    const void *descriptor
)
{
    return open_cfw_test_format_value_adapter(output, descriptor, 6U);
}

unsigned int open_cfw_format_span(
    void *output,
    const void *descriptor
)
{
    return open_cfw_test_format_value_adapter(output, descriptor, 7U);
}

void open_cfw_test_format_value_set_error(
    void *output,
    unsigned int error
)
{
    unsigned int *current =
        (unsigned int *)(void *)((unsigned char *)output + 0x10U);

    open_cfw_test_format_value_error_calls += 1U;
    open_cfw_test_format_value_last_error = error;
    if (*current == 0U) {
        *current = error;
    }
}

#define OPEN_CFW_FORMAT_VALUE_TYPE(descriptor) \
    (open_cfw_test_format_value_type)
#define OPEN_CFW_FORMAT_VALUE_DATA(descriptor) \
    (open_cfw_test_format_value_data)
#define OPEN_CFW_FORMAT_VALUE_SET_ERROR(output, error) \
    open_cfw_test_format_value_set_error((output), (error))

#include "../../components/apollo_main/core_overlay/format_value.c"
