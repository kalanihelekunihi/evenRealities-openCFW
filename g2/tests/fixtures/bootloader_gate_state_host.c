static unsigned int open_cfw_test_state;
static unsigned int open_cfw_test_gate;
static unsigned int open_cfw_test_state_calls;
static unsigned int open_cfw_test_gate_reads;

static unsigned int open_cfw_test_runtime_state(void)
{
    open_cfw_test_state_calls += 1U;
    return open_cfw_test_state;
}

static unsigned int open_cfw_test_gate_word(void)
{
    open_cfw_test_gate_reads += 1U;
    return open_cfw_test_gate;
}

#define OPEN_CFW_BOOTLOADER_RUNTIME_STATE() open_cfw_test_runtime_state()
#define OPEN_CFW_BOOTLOADER_GATE_WORD open_cfw_test_gate_word()
#include "../../components/bootloader/core_overlay/runtime_gate_state.c"

void open_cfw_test_gate_state_set(unsigned int state, unsigned int gate)
{
    open_cfw_test_state = state;
    open_cfw_test_gate = gate;
    open_cfw_test_state_calls = 0U;
    open_cfw_test_gate_reads = 0U;
}

unsigned int open_cfw_test_gate_state_calls(void)
{
    return open_cfw_test_state_calls;
}

unsigned int open_cfw_test_gate_state_reads(void)
{
    return open_cfw_test_gate_reads;
}
