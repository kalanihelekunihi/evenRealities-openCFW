#include <stdint.h>

unsigned int open_cfw_test_format_field_prefix_result;
unsigned int open_cfw_test_format_field_prefix_calls;
void *open_cfw_test_format_field_prefix_output;
unsigned long long open_cfw_test_format_field_prefix_value;
unsigned int open_cfw_test_format_field_invalid_calls;
void *open_cfw_test_format_field_invalid_output;
uintptr_t open_cfw_test_format_field_error;

void open_cfw_test_format_field_reset(void)
{
    open_cfw_test_format_field_prefix_result = 1U;
    open_cfw_test_format_field_prefix_calls = 0U;
    open_cfw_test_format_field_prefix_output = (void *)0;
    open_cfw_test_format_field_prefix_value = 0U;
    open_cfw_test_format_field_invalid_calls = 0U;
    open_cfw_test_format_field_invalid_output = (void *)0;
    open_cfw_test_format_field_error = 0U;
}

unsigned int open_cfw_test_format_field_prefix(
    void *output,
    unsigned long long value
)
{
    open_cfw_test_format_field_prefix_calls += 1U;
    open_cfw_test_format_field_prefix_output = output;
    open_cfw_test_format_field_prefix_value = value;
    return open_cfw_test_format_field_prefix_result;
}

void open_cfw_test_format_field_invalid(void *output)
{
    open_cfw_test_format_field_invalid_calls += 1U;
    open_cfw_test_format_field_invalid_output = output;
    if (open_cfw_test_format_field_error == 0U) {
        open_cfw_test_format_field_error = 0x00781854U;
    }
}

#define OPEN_CFW_FORMAT_FIELD_PREFIX(output, value) \
    open_cfw_test_format_field_prefix((output), (value))
#define OPEN_CFW_FORMAT_FIELD_SET_INVALID(output) \
    open_cfw_test_format_field_invalid((output))

#include "../../components/apollo_main/core_overlay/format_field.c"
