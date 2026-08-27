static unsigned int open_cfw_test_runtime_value;
static unsigned int open_cfw_test_runtime_value_calls;

static unsigned int open_cfw_test_runtime_value_418b4e(void)
{
    open_cfw_test_runtime_value_calls += 1U;
    return open_cfw_test_runtime_value;
}

#define OPEN_CFW_BOOTLOADER_RUNTIME_VALUE_418B4E() \
    open_cfw_test_runtime_value_418b4e()
#include "../../components/bootloader/core_overlay/runtime_value_4161c6.c"

void open_cfw_test_runtime_value_set(unsigned int value)
{
    open_cfw_test_runtime_value = value;
    open_cfw_test_runtime_value_calls = 0U;
}

unsigned int open_cfw_test_runtime_value_calls_get(void)
{
    return open_cfw_test_runtime_value_calls;
}
