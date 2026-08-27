static unsigned int open_cfw_test_critical_context;
static unsigned int open_cfw_test_critical_context_calls;
static unsigned int open_cfw_test_retained_calls;
static unsigned int open_cfw_test_retained_argument_0;
static unsigned int open_cfw_test_retained_argument_1;

static unsigned int open_cfw_test_critical_context_get(void)
{
    open_cfw_test_critical_context_calls += 1U;
    return open_cfw_test_critical_context;
}

static void open_cfw_test_runtime_call_41806e(
    unsigned int argument_0,
    unsigned int argument_1
)
{
    open_cfw_test_retained_calls += 1U;
    open_cfw_test_retained_argument_0 = argument_0;
    open_cfw_test_retained_argument_1 = argument_1;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_test_critical_context_get()
#define OPEN_CFW_BOOTLOADER_RUNTIME_CALL_41806E(...) \
    open_cfw_test_runtime_call_41806e(__VA_ARGS__)
#include "../../components/bootloader/core_overlay/runtime_call_4161ce.c"

void open_cfw_test_runtime_call_reset(unsigned int critical_context)
{
    open_cfw_test_critical_context = critical_context;
    open_cfw_test_critical_context_calls = 0U;
    open_cfw_test_retained_calls = 0U;
    open_cfw_test_retained_argument_0 = 0U;
    open_cfw_test_retained_argument_1 = 0U;
}

unsigned int open_cfw_test_critical_context_calls_get(void)
{
    return open_cfw_test_critical_context_calls;
}

unsigned int open_cfw_test_retained_calls_get(void)
{
    return open_cfw_test_retained_calls;
}

unsigned int open_cfw_test_retained_argument_0_get(void)
{
    return open_cfw_test_retained_argument_0;
}

unsigned int open_cfw_test_retained_argument_1_get(void)
{
    return open_cfw_test_retained_argument_1;
}
