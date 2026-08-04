#include <stdint.h>

struct open_cfw_test_format_repeated_field {
    unsigned int type;
    unsigned int tag;
    unsigned int element_size;
    unsigned int max_count;
    void *data;
    unsigned int count;
};

void *open_cfw_test_format_repeated_main_output;
unsigned int open_cfw_test_format_repeated_field_key_result;
unsigned int open_cfw_test_format_repeated_prefix_result;
unsigned int open_cfw_test_format_repeated_append_result;
unsigned int open_cfw_test_format_repeated_integer_result;
unsigned int open_cfw_test_format_repeated_fixed_result;
unsigned int open_cfw_test_format_repeated_descriptor_result;
unsigned int open_cfw_test_format_repeated_value_result;
unsigned int open_cfw_test_format_repeated_sizing_bytes;
unsigned int open_cfw_test_format_repeated_sizing_fail_call;
unsigned int open_cfw_test_format_repeated_encode_fail_call;
unsigned int open_cfw_test_format_repeated_field_key_calls;
unsigned int open_cfw_test_format_repeated_prefix_calls;
unsigned int open_cfw_test_format_repeated_append_calls;
unsigned int open_cfw_test_format_repeated_sizing_calls;
unsigned int open_cfw_test_format_repeated_integer_calls;
unsigned int open_cfw_test_format_repeated_fixed_calls;
unsigned int open_cfw_test_format_repeated_descriptor_calls;
unsigned int open_cfw_test_format_repeated_value_calls;
unsigned int open_cfw_test_format_repeated_last_wire_type;
unsigned int open_cfw_test_format_repeated_last_tag;
unsigned long long open_cfw_test_format_repeated_last_prefix;
const void *open_cfw_test_format_repeated_last_append_data;
unsigned int open_cfw_test_format_repeated_last_append_length;
const void *open_cfw_test_format_repeated_last_value_data;
const char *open_cfw_test_format_repeated_sizing_error;

void open_cfw_test_format_repeated_reset(void)
{
    open_cfw_test_format_repeated_main_output = (void *)0;
    open_cfw_test_format_repeated_field_key_result = 1U;
    open_cfw_test_format_repeated_prefix_result = 1U;
    open_cfw_test_format_repeated_append_result = 1U;
    open_cfw_test_format_repeated_integer_result = 1U;
    open_cfw_test_format_repeated_fixed_result = 1U;
    open_cfw_test_format_repeated_descriptor_result = 1U;
    open_cfw_test_format_repeated_value_result = 1U;
    open_cfw_test_format_repeated_sizing_bytes = 1U;
    open_cfw_test_format_repeated_sizing_fail_call = 0U;
    open_cfw_test_format_repeated_encode_fail_call = 0U;
    open_cfw_test_format_repeated_field_key_calls = 0U;
    open_cfw_test_format_repeated_prefix_calls = 0U;
    open_cfw_test_format_repeated_append_calls = 0U;
    open_cfw_test_format_repeated_sizing_calls = 0U;
    open_cfw_test_format_repeated_integer_calls = 0U;
    open_cfw_test_format_repeated_fixed_calls = 0U;
    open_cfw_test_format_repeated_descriptor_calls = 0U;
    open_cfw_test_format_repeated_value_calls = 0U;
    open_cfw_test_format_repeated_last_wire_type = 0U;
    open_cfw_test_format_repeated_last_tag = 0U;
    open_cfw_test_format_repeated_last_prefix = 0ULL;
    open_cfw_test_format_repeated_last_append_data = (const void *)0;
    open_cfw_test_format_repeated_last_append_length = 0U;
    open_cfw_test_format_repeated_last_value_data = (const void *)0;
    open_cfw_test_format_repeated_sizing_error = (const char *)0;
}

#define OPEN_CFW_FORMAT_REPEATED_TYPE(field) \
    (((const struct open_cfw_test_format_repeated_field *)(field))->type)
#define OPEN_CFW_FORMAT_REPEATED_TAG(field) \
    (((const struct open_cfw_test_format_repeated_field *)(field))->tag)
#define OPEN_CFW_FORMAT_REPEATED_ELEMENT_SIZE(field) \
    (((const struct open_cfw_test_format_repeated_field *)(field))->element_size)
#define OPEN_CFW_FORMAT_REPEATED_MAX_COUNT(field) \
    (((const struct open_cfw_test_format_repeated_field *)(field))->max_count)
#define OPEN_CFW_FORMAT_REPEATED_DATA(field) \
    (((const struct open_cfw_test_format_repeated_field *)(field))->data)
#define OPEN_CFW_FORMAT_REPEATED_SET_DATA(field, value) \
    (((struct open_cfw_test_format_repeated_field *)(field))->data = (void *)(value))
#define OPEN_CFW_FORMAT_REPEATED_COUNT(field) \
    (((const struct open_cfw_test_format_repeated_field *)(field))->count)

#include "../../components/apollo_main/core_overlay/format_repeated.c"

unsigned int open_cfw_format_field_key_write(
    void *output,
    unsigned int wire_type,
    unsigned int field_number
)
{
    (void)output;
    open_cfw_test_format_repeated_field_key_calls += 1U;
    open_cfw_test_format_repeated_last_wire_type = wire_type;
    open_cfw_test_format_repeated_last_tag = field_number;
    return open_cfw_test_format_repeated_field_key_result;
}

unsigned int open_cfw_format_descriptor_key_write(
    void *output,
    const void *descriptor
)
{
    (void)output;
    (void)descriptor;
    open_cfw_test_format_repeated_descriptor_calls += 1U;
    return open_cfw_test_format_repeated_descriptor_result;
}

unsigned int open_cfw_format_u64_prefix_write(
    void *output,
    unsigned long long value
)
{
    (void)output;
    open_cfw_test_format_repeated_prefix_calls += 1U;
    open_cfw_test_format_repeated_last_prefix = value;
    return open_cfw_test_format_repeated_prefix_result;
}

unsigned int open_cfw_format_append(
    void *output,
    const void *data,
    unsigned int length
)
{
    (void)output;
    open_cfw_test_format_repeated_append_calls += 1U;
    open_cfw_test_format_repeated_last_append_data = data;
    open_cfw_test_format_repeated_last_append_length = length;
    return open_cfw_test_format_repeated_append_result;
}

unsigned int open_cfw_format_integer_write(
    void *output,
    const void *descriptor
)
{
    (void)descriptor;
    if (output != open_cfw_test_format_repeated_main_output) {
        struct open_cfw_format_repeated_output *sizing =
            (struct open_cfw_format_repeated_output *)output;

        open_cfw_test_format_repeated_sizing_calls += 1U;
        if (
            open_cfw_test_format_repeated_sizing_fail_call
            == open_cfw_test_format_repeated_sizing_calls
        ) {
            sizing->error = open_cfw_test_format_repeated_sizing_error;
            return 0U;
        }
        sizing->length += open_cfw_test_format_repeated_sizing_bytes;
        return 1U;
    }
    open_cfw_test_format_repeated_integer_calls += 1U;
    if (
        open_cfw_test_format_repeated_encode_fail_call
        == open_cfw_test_format_repeated_integer_calls
    ) {
        return 0U;
    }
    return open_cfw_test_format_repeated_integer_result;
}

unsigned int open_cfw_format_fixed_write(
    void *output,
    const void *descriptor
)
{
    (void)output;
    (void)descriptor;
    open_cfw_test_format_repeated_fixed_calls += 1U;
    if (
        open_cfw_test_format_repeated_encode_fail_call
        == open_cfw_test_format_repeated_fixed_calls
    ) {
        return 0U;
    }
    return open_cfw_test_format_repeated_fixed_result;
}

unsigned int open_cfw_format_value_encode(
    void *output,
    const void *descriptor
)
{
    const struct open_cfw_test_format_repeated_field *field =
        (const struct open_cfw_test_format_repeated_field *)descriptor;

    (void)output;
    open_cfw_test_format_repeated_value_calls += 1U;
    open_cfw_test_format_repeated_last_value_data = field->data;
    if (
        open_cfw_test_format_repeated_encode_fail_call
        == open_cfw_test_format_repeated_value_calls
    ) {
        return 0U;
    }
    return open_cfw_test_format_repeated_value_result;
}
