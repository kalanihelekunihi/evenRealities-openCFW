static unsigned int open_cfw_test_critical;
static unsigned int open_cfw_test_normal_value;
static unsigned int open_cfw_test_critical_value;
static unsigned int open_cfw_test_context_calls;
static unsigned int open_cfw_test_normal_calls;
static unsigned int open_cfw_test_critical_value_calls;

static unsigned int open_cfw_test_context(void)
{
    open_cfw_test_context_calls += 1U;
    return open_cfw_test_critical;
}

static unsigned int open_cfw_test_normal(void)
{
    open_cfw_test_normal_calls += 1U;
    return open_cfw_test_normal_value;
}

static unsigned int open_cfw_test_critical_getter(void)
{
    open_cfw_test_critical_value_calls += 1U;
    return open_cfw_test_critical_value;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_context()
#define OPEN_CFW_BOOTLOADER_NORMAL_CONTEXT_VALUE() open_cfw_test_normal()
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT_VALUE() open_cfw_test_critical_getter()
#include "../../components/bootloader/core_overlay/runtime_context_value.c"

void open_cfw_test_context_value_set(
    unsigned int critical,
    unsigned int normal_value,
    unsigned int critical_value
)
{
    open_cfw_test_critical = critical;
    open_cfw_test_normal_value = normal_value;
    open_cfw_test_critical_value = critical_value;
    open_cfw_test_context_calls = 0U;
    open_cfw_test_normal_calls = 0U;
    open_cfw_test_critical_value_calls = 0U;
}

unsigned int open_cfw_test_context_value_context_calls(void) { return open_cfw_test_context_calls; }
unsigned int open_cfw_test_context_value_normal_calls(void) { return open_cfw_test_normal_calls; }
unsigned int open_cfw_test_context_value_critical_calls(void) { return open_cfw_test_critical_value_calls; }
