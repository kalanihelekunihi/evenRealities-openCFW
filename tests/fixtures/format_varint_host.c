unsigned int open_cfw_test_format_varint_append_result;
unsigned int open_cfw_test_format_varint_append_calls;
void *open_cfw_test_format_varint_append_output;
unsigned int open_cfw_test_format_varint_append_length;
unsigned char open_cfw_test_format_varint_append_data[10];

void open_cfw_test_format_varint_reset(void)
{
    unsigned int index;

    open_cfw_test_format_varint_append_result = 1U;
    open_cfw_test_format_varint_append_calls = 0U;
    open_cfw_test_format_varint_append_output = (void *)0;
    open_cfw_test_format_varint_append_length = 0U;
    for (index = 0U; index < 10U; index += 1U) {
        open_cfw_test_format_varint_append_data[index] = 0U;
    }
}

unsigned int open_cfw_test_format_varint_append(
    void *output,
    const void *data,
    unsigned int length
)
{
    const unsigned char *bytes = (const unsigned char *)data;
    unsigned int index;

    open_cfw_test_format_varint_append_calls += 1U;
    open_cfw_test_format_varint_append_output = output;
    open_cfw_test_format_varint_append_length = length;
    for (index = 0U; (index < length) && (index < 10U); index += 1U) {
        open_cfw_test_format_varint_append_data[index] = bytes[index];
    }
    return open_cfw_test_format_varint_append_result;
}

#define OPEN_CFW_FORMAT_VARINT_APPEND(output, data, length) \
    open_cfw_test_format_varint_append((output), (data), (length))

#include "../../components/apollo_main/core_overlay/format_varint.c"
