static unsigned int open_cfw_test_ipsr;
static unsigned int open_cfw_test_primask;
static unsigned int open_cfw_test_basepri;
static unsigned int open_cfw_test_runtime_state;
static unsigned int open_cfw_test_runtime_calls;

static unsigned int open_cfw_test_runtime_state_query(void)
{
    open_cfw_test_runtime_calls += 1U;
    return open_cfw_test_runtime_state;
}

#define OPEN_CFW_BOOTLOADER_READ_IPSR() open_cfw_test_ipsr
#define OPEN_CFW_BOOTLOADER_READ_PRIMASK() open_cfw_test_primask
#define OPEN_CFW_BOOTLOADER_READ_BASEPRI() open_cfw_test_basepri
#define OPEN_CFW_BOOTLOADER_RUNTIME_STATE() \
    open_cfw_test_runtime_state_query()
#include "../../components/bootloader/core_overlay/runtime_critical_context.c"

void open_cfw_test_critical_context_set(
    unsigned int ipsr,
    unsigned int state,
    unsigned int primask,
    unsigned int basepri
)
{
    open_cfw_test_ipsr = ipsr;
    open_cfw_test_runtime_state = state;
    open_cfw_test_primask = primask;
    open_cfw_test_basepri = basepri;
    open_cfw_test_runtime_calls = 0U;
}

unsigned int open_cfw_test_critical_context_runtime_calls(void)
{
    return open_cfw_test_runtime_calls;
}
