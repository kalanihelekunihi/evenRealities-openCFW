#include <stdint.h>

unsigned int open_cfw_test_format_scalar_result;
unsigned int open_cfw_test_format_scalar_calls;
unsigned int open_cfw_test_format_scalar_kind;
void *open_cfw_test_format_scalar_output;
const void *open_cfw_test_format_scalar_data;
unsigned long long open_cfw_test_format_scalar_value;
long long open_cfw_test_format_scalar_signed_value;
unsigned int open_cfw_test_format_scalar_invalid_calls;
void *open_cfw_test_format_scalar_invalid_output;
uintptr_t open_cfw_test_format_scalar_error;

void open_cfw_test_format_scalar_reset(void)
{
    open_cfw_test_format_scalar_result = 1U;
    open_cfw_test_format_scalar_calls = 0U;
    open_cfw_test_format_scalar_kind = 0U;
    open_cfw_test_format_scalar_output = (void *)0;
    open_cfw_test_format_scalar_data = (const void *)0;
    open_cfw_test_format_scalar_value = 0U;
    open_cfw_test_format_scalar_signed_value = 0;
    open_cfw_test_format_scalar_invalid_calls = 0U;
    open_cfw_test_format_scalar_invalid_output = (void *)0;
    open_cfw_test_format_scalar_error = 0U;
}

unsigned int open_cfw_test_format_scalar_prefix(
    void *output,
    unsigned long long value
)
{
    open_cfw_test_format_scalar_calls += 1U;
    open_cfw_test_format_scalar_kind = 1U;
    open_cfw_test_format_scalar_output = output;
    open_cfw_test_format_scalar_value = value;
    return open_cfw_test_format_scalar_result;
}

unsigned int open_cfw_test_format_scalar_zigzag(
    void *output,
    long long value
)
{
    open_cfw_test_format_scalar_calls += 1U;
    open_cfw_test_format_scalar_kind = 2U;
    open_cfw_test_format_scalar_output = output;
    open_cfw_test_format_scalar_signed_value = value;
    return open_cfw_test_format_scalar_result;
}

unsigned int open_cfw_test_format_scalar_fixed(
    void *output,
    const void *data,
    unsigned int kind
)
{
    open_cfw_test_format_scalar_calls += 1U;
    open_cfw_test_format_scalar_kind = kind;
    open_cfw_test_format_scalar_output = output;
    open_cfw_test_format_scalar_data = data;
    return open_cfw_test_format_scalar_result;
}

void open_cfw_test_format_scalar_invalid(void *output)
{
    open_cfw_test_format_scalar_invalid_calls += 1U;
    open_cfw_test_format_scalar_invalid_output = output;
    if (open_cfw_test_format_scalar_error == 0U) {
        open_cfw_test_format_scalar_error = 0x00781890U;
    }
}

#define OPEN_CFW_FORMAT_SCALAR_PREFIX(output, value) \
    open_cfw_test_format_scalar_prefix((output), (value))
#define OPEN_CFW_FORMAT_SCALAR_ZIGZAG(output, value) \
    open_cfw_test_format_scalar_zigzag((output), (value))
#define OPEN_CFW_FORMAT_SCALAR_FIXED4(output, data) \
    open_cfw_test_format_scalar_fixed((output), (data), 4U)
#define OPEN_CFW_FORMAT_SCALAR_FIXED8(output, data) \
    open_cfw_test_format_scalar_fixed((output), (data), 8U)
#define OPEN_CFW_FORMAT_SCALAR_SET_INVALID_SIZE(output) \
    open_cfw_test_format_scalar_invalid((output))

#include "../../components/apollo_main/core_overlay/format_scalar.c"
