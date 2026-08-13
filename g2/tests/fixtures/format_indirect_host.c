#include <stdint.h>

unsigned int open_cfw_test_format_indirect_callback_enabled;
unsigned int open_cfw_test_format_indirect_callback_result;
unsigned int open_cfw_test_format_indirect_callback_calls;
unsigned int open_cfw_test_format_indirect_error_calls;
unsigned int open_cfw_test_format_indirect_last_error;
void *open_cfw_test_format_indirect_callback_argument;
void *open_cfw_test_format_indirect_callback_output;

void open_cfw_test_format_indirect_reset(void)
{
    open_cfw_test_format_indirect_callback_enabled = 0U;
    open_cfw_test_format_indirect_callback_result = 1U;
    open_cfw_test_format_indirect_callback_calls = 0U;
    open_cfw_test_format_indirect_error_calls = 0U;
    open_cfw_test_format_indirect_last_error = 0U;
    open_cfw_test_format_indirect_callback_argument = (void *)0;
    open_cfw_test_format_indirect_callback_output = (void *)0;
}

unsigned int open_cfw_test_format_indirect_callback(
    void *argument,
    void *output
)
{
    open_cfw_test_format_indirect_callback_calls += 1U;
    open_cfw_test_format_indirect_callback_argument = argument;
    open_cfw_test_format_indirect_callback_output = output;
    return open_cfw_test_format_indirect_callback_result;
}

void open_cfw_test_format_indirect_set_error(
    void *output,
    unsigned int error
)
{
    unsigned int *current =
        (unsigned int *)(void *)((unsigned char *)output + 0x10U);

    open_cfw_test_format_indirect_error_calls += 1U;
    open_cfw_test_format_indirect_last_error = error;
    if (*current == 0U) {
        *current = error;
    }
}

#define OPEN_CFW_FORMAT_INDIRECT_CALLBACK(field) \
    ((void)(field), \
        (open_cfw_test_format_indirect_callback_enabled != 0U \
            ? open_cfw_test_format_indirect_callback \
            : (open_cfw_format_indirect_callback_fn)0))
#define OPEN_CFW_FORMAT_INDIRECT_SET_ERROR(output, error) \
    open_cfw_test_format_indirect_set_error((output), (error))

#include "../../components/apollo_main/core_overlay/format_indirect.c"
