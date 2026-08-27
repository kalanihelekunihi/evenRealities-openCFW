static unsigned int open_cfw_test_critical_context;
static unsigned int open_cfw_test_predicate_result;
static unsigned int open_cfw_test_critical_calls;
static unsigned int open_cfw_test_predicate_calls;
static unsigned int open_cfw_test_action_calls;
static unsigned int open_cfw_test_predicate_argument;
static unsigned int open_cfw_test_action_argument;

static unsigned int open_cfw_test_critical_context_get(void)
{
    open_cfw_test_critical_calls += 1U;
    return open_cfw_test_critical_context;
}

static unsigned int open_cfw_test_runtime_predicate_417fe4(unsigned int value)
{
    open_cfw_test_predicate_calls += 1U;
    open_cfw_test_predicate_argument = value;
    return open_cfw_test_predicate_result;
}

static void open_cfw_test_runtime_action_417f0a(unsigned int value)
{
    open_cfw_test_action_calls += 1U;
    open_cfw_test_action_argument = value;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_test_critical_context_get()
#define OPEN_CFW_BOOTLOADER_RUNTIME_PREDICATE_417FE4(argument_0) \
    open_cfw_test_runtime_predicate_417fe4(argument_0)
#define OPEN_CFW_BOOTLOADER_RUNTIME_ACTION_417F0A(argument_0) \
    open_cfw_test_runtime_action_417f0a(argument_0)
#include "../../components/bootloader/core_overlay/runtime_action_416200.c"

void open_cfw_test_runtime_action_reset(
    unsigned int critical_context,
    unsigned int predicate_result
)
{
    open_cfw_test_critical_context = critical_context;
    open_cfw_test_predicate_result = predicate_result;
    open_cfw_test_critical_calls = 0U;
    open_cfw_test_predicate_calls = 0U;
    open_cfw_test_action_calls = 0U;
    open_cfw_test_predicate_argument = 0U;
    open_cfw_test_action_argument = 0U;
}

unsigned int open_cfw_test_critical_calls_get(void) { return open_cfw_test_critical_calls; }
unsigned int open_cfw_test_predicate_calls_get(void) { return open_cfw_test_predicate_calls; }
unsigned int open_cfw_test_action_calls_get(void) { return open_cfw_test_action_calls; }
unsigned int open_cfw_test_predicate_argument_get(void) { return open_cfw_test_predicate_argument; }
unsigned int open_cfw_test_action_argument_get(void) { return open_cfw_test_action_argument; }
