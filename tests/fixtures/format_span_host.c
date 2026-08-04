struct __attribute__((packed)) open_cfw_test_format_argument {
    unsigned char before_length[0x12];
    unsigned short length;
    unsigned char before_data[8];
    const void *data;
};

unsigned int open_cfw_test_format_span_calls;
void *open_cfw_test_format_span_output;
const void *open_cfw_test_format_span_data;
unsigned int open_cfw_test_format_span_length;
unsigned int open_cfw_test_format_span_result;

unsigned int open_cfw_test_format_span_write(
    void *output,
    const void *data,
    unsigned int length
)
{
    ++open_cfw_test_format_span_calls;
    open_cfw_test_format_span_output = output;
    open_cfw_test_format_span_data = data;
    open_cfw_test_format_span_length = length;
    return open_cfw_test_format_span_result;
}

#define OPEN_CFW_FORMAT_SPAN_HOST 1
#define OPEN_CFW_FORMAT_SPAN_LENGTH(argument) \
    (((const struct open_cfw_test_format_argument *)(argument))->length)
#define OPEN_CFW_FORMAT_SPAN_DATA(argument) \
    (((const struct open_cfw_test_format_argument *)(argument))->data)
#define OPEN_CFW_FORMAT_SPAN_WRITE(output, data, length) \
    open_cfw_test_format_span_write((output), (data), (length))

#include "../../components/apollo_main/core_overlay/format_span.c"
