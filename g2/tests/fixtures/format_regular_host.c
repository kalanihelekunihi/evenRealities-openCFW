#include <stdint.h>

unsigned int open_cfw_test_format_regular_type;
unsigned int open_cfw_test_format_regular_tag;
unsigned int open_cfw_test_format_regular_aux_tag;
unsigned int open_cfw_test_format_regular_bool_result;
unsigned int open_cfw_test_format_regular_default_result;
unsigned int open_cfw_test_format_regular_indirect_result;
unsigned int open_cfw_test_format_regular_repeated_result;
unsigned int open_cfw_test_format_regular_value_result;
unsigned int open_cfw_test_format_regular_bool_calls;
unsigned int open_cfw_test_format_regular_default_calls;
unsigned int open_cfw_test_format_regular_indirect_calls;
unsigned int open_cfw_test_format_regular_repeated_calls;
unsigned int open_cfw_test_format_regular_value_calls;
unsigned int open_cfw_test_format_regular_error_calls;
unsigned int open_cfw_test_format_regular_last_error;
const void *open_cfw_test_format_regular_data;
const void *open_cfw_test_format_regular_aux;
const void *open_cfw_test_format_regular_bool_value;
const void *open_cfw_test_format_regular_default_field;
void *open_cfw_test_format_regular_last_output;
const void *open_cfw_test_format_regular_last_field;

void open_cfw_test_format_regular_reset(void)
{
    open_cfw_test_format_regular_type = 0U;
    open_cfw_test_format_regular_tag = 0U;
    open_cfw_test_format_regular_aux_tag = 0U;
    open_cfw_test_format_regular_bool_result = 1U;
    open_cfw_test_format_regular_default_result = 0U;
    open_cfw_test_format_regular_indirect_result = 1U;
    open_cfw_test_format_regular_repeated_result = 1U;
    open_cfw_test_format_regular_value_result = 1U;
    open_cfw_test_format_regular_bool_calls = 0U;
    open_cfw_test_format_regular_default_calls = 0U;
    open_cfw_test_format_regular_indirect_calls = 0U;
    open_cfw_test_format_regular_repeated_calls = 0U;
    open_cfw_test_format_regular_value_calls = 0U;
    open_cfw_test_format_regular_error_calls = 0U;
    open_cfw_test_format_regular_last_error = 0U;
    open_cfw_test_format_regular_data = (const void *)0x11112222U;
    open_cfw_test_format_regular_aux = (const void *)0;
    open_cfw_test_format_regular_bool_value = (const void *)0;
    open_cfw_test_format_regular_default_field = (const void *)0;
    open_cfw_test_format_regular_last_output = (void *)0;
    open_cfw_test_format_regular_last_field = (const void *)0;
}

unsigned int open_cfw_test_format_regular_read_bool(const void *value)
{
    open_cfw_test_format_regular_bool_calls += 1U;
    open_cfw_test_format_regular_bool_value = value;
    return open_cfw_test_format_regular_bool_result;
}

unsigned int open_cfw_test_format_regular_default_check(const void *field)
{
    open_cfw_test_format_regular_default_calls += 1U;
    open_cfw_test_format_regular_default_field = field;
    return open_cfw_test_format_regular_default_result;
}

static unsigned int open_cfw_test_format_regular_encode(
    void *output,
    const void *field,
    unsigned int kind
)
{
    open_cfw_test_format_regular_last_output = output;
    open_cfw_test_format_regular_last_field = field;
    if (kind == 1U) {
        open_cfw_test_format_regular_indirect_calls += 1U;
        return open_cfw_test_format_regular_indirect_result;
    }
    if (kind == 2U) {
        open_cfw_test_format_regular_repeated_calls += 1U;
        return open_cfw_test_format_regular_repeated_result;
    }
    open_cfw_test_format_regular_value_calls += 1U;
    return open_cfw_test_format_regular_value_result;
}

void open_cfw_test_format_regular_set_error(
    void *output,
    unsigned int error
)
{
    unsigned int *current =
        (unsigned int *)(void *)((unsigned char *)output + 0x10U);

    open_cfw_test_format_regular_error_calls += 1U;
    open_cfw_test_format_regular_last_error = error;
    if (*current == 0U) {
        *current = error;
    }
}

#define OPEN_CFW_FORMAT_REGULAR_TYPE(field) \
    (open_cfw_test_format_regular_type)
#define OPEN_CFW_FORMAT_REGULAR_TAG(field) \
    (open_cfw_test_format_regular_tag)
#define OPEN_CFW_FORMAT_REGULAR_DATA(field) \
    (open_cfw_test_format_regular_data)
#define OPEN_CFW_FORMAT_REGULAR_AUX(field) \
    (open_cfw_test_format_regular_aux)
#define OPEN_CFW_FORMAT_REGULAR_AUX_TAG(aux) \
    (open_cfw_test_format_regular_aux_tag)
#define OPEN_CFW_FORMAT_REGULAR_READ_BOOL(value) \
    open_cfw_test_format_regular_read_bool((value))
#define OPEN_CFW_FORMAT_REGULAR_DEFAULT_CHECK(field) \
    open_cfw_test_format_regular_default_check((field))
#define OPEN_CFW_FORMAT_REGULAR_INDIRECT_ENCODE(output, field) \
    open_cfw_test_format_regular_encode((output), (field), 1U)
#define OPEN_CFW_FORMAT_REGULAR_REPEATED_ENCODE(output, field) \
    open_cfw_test_format_regular_encode((output), (field), 2U)
#define OPEN_CFW_FORMAT_REGULAR_VALUE_ENCODE(output, field) \
    open_cfw_test_format_regular_encode((output), (field), 3U)
#define OPEN_CFW_FORMAT_REGULAR_SET_ERROR(output, error) \
    open_cfw_test_format_regular_set_error((output), (error))

#include "../../components/apollo_main/core_overlay/format_regular.c"
