static unsigned int open_cfw_test_critical;
static unsigned int open_cfw_test_state;
static unsigned int open_cfw_test_gate;
static unsigned int open_cfw_test_critical_calls;
static unsigned int open_cfw_test_state_calls;

static unsigned int open_cfw_test_critical_context(void)
{
    open_cfw_test_critical_calls += 1U;
    return open_cfw_test_critical;
}

static unsigned int open_cfw_test_runtime_state(void)
{
    open_cfw_test_state_calls += 1U;
    return open_cfw_test_state;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_test_critical_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_STATE() open_cfw_test_runtime_state()
#define OPEN_CFW_BOOTLOADER_GATE_WORD open_cfw_test_gate
#include "../../components/bootloader/core_overlay/runtime_gate_acquire.c"

void open_cfw_test_gate_set(
    unsigned int critical,
    unsigned int state,
    unsigned int gate
)
{
    open_cfw_test_critical = critical;
    open_cfw_test_state = state;
    open_cfw_test_gate = gate;
    open_cfw_test_critical_calls = 0U;
    open_cfw_test_state_calls = 0U;
}

unsigned int open_cfw_test_gate_word(void) { return open_cfw_test_gate; }
unsigned int open_cfw_test_gate_critical_calls(void)
{
    return open_cfw_test_critical_calls;
}
unsigned int open_cfw_test_gate_state_calls(void)
{
    return open_cfw_test_state_calls;
}
