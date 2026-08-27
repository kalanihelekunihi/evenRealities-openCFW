static unsigned int open_cfw_test_critical;
static unsigned int open_cfw_test_state;
static unsigned int open_cfw_test_gate;
static unsigned int open_cfw_test_critical_calls;
static unsigned int open_cfw_test_state_calls;
static unsigned int open_cfw_test_transition_calls;
static unsigned int open_cfw_test_complete_calls;
static unsigned int open_cfw_test_order;

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

static void open_cfw_test_transition_hook(void)
{
    open_cfw_test_transition_calls += 1U;
    open_cfw_test_order = open_cfw_test_order * 10U + 1U;
}

static void open_cfw_test_complete(void)
{
    open_cfw_test_complete_calls += 1U;
    open_cfw_test_order = open_cfw_test_order * 10U +
        (open_cfw_test_gate == 2U ? 2U : 9U);
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_critical_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_STATE() open_cfw_test_runtime_state()
#define OPEN_CFW_BOOTLOADER_GATE_WORD open_cfw_test_gate
#define OPEN_CFW_BOOTLOADER_GATE_TRANSITION_HOOK() open_cfw_test_transition_hook()
#define OPEN_CFW_BOOTLOADER_GATE_COMPLETE() open_cfw_test_complete()
#include "../../components/bootloader/core_overlay/runtime_gate_release.c"

void open_cfw_test_gate_release_set(
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
    open_cfw_test_transition_calls = 0U;
    open_cfw_test_complete_calls = 0U;
    open_cfw_test_order = 0U;
}

unsigned int open_cfw_test_gate_release_gate(void) { return open_cfw_test_gate; }
unsigned int open_cfw_test_gate_release_critical_calls(void) { return open_cfw_test_critical_calls; }
unsigned int open_cfw_test_gate_release_state_calls(void) { return open_cfw_test_state_calls; }
unsigned int open_cfw_test_gate_release_transition_calls(void) { return open_cfw_test_transition_calls; }
unsigned int open_cfw_test_gate_release_complete_calls(void) { return open_cfw_test_complete_calls; }
unsigned int open_cfw_test_gate_release_order(void) { return open_cfw_test_order; }
