unsigned int open_cfw_test_format_fixed_result;
unsigned int open_cfw_test_format_fixed_calls;
void *open_cfw_test_format_fixed_output;
const void *open_cfw_test_format_fixed_data;
unsigned int open_cfw_test_format_fixed_length;

void open_cfw_test_format_fixed_reset(void)
{
    open_cfw_test_format_fixed_result = 1U;
    open_cfw_test_format_fixed_calls = 0U;
    open_cfw_test_format_fixed_output = (void *)0;
    open_cfw_test_format_fixed_data = (const void *)0;
    open_cfw_test_format_fixed_length = 0U;
}

unsigned int open_cfw_test_format_fixed_append(
    void *output,
    const void *data,
    unsigned int length
)
{
    open_cfw_test_format_fixed_calls += 1U;
    open_cfw_test_format_fixed_output = output;
    open_cfw_test_format_fixed_data = data;
    open_cfw_test_format_fixed_length = length;
    return open_cfw_test_format_fixed_result;
}

#define OPEN_CFW_FORMAT_FIXED_APPEND(output, data, length) \
    open_cfw_test_format_fixed_append((output), (data), (length))

#include "../../components/apollo_main/core_overlay/format_fixed.c"
