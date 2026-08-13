#include <stdint.h>

uint32_t open_cfw_test_syspll_enabled_pllctl0;
uint32_t open_cfw_test_syspll_enabled_output;
uint32_t open_cfw_test_syspll_enabled_read_count;
uint32_t open_cfw_test_syspll_enabled_read_address;

static uint32_t
open_cfw_test_syspll_enabled_read32(uint32_t address)
{
    ++open_cfw_test_syspll_enabled_read_count;
    open_cfw_test_syspll_enabled_read_address = address;
    return open_cfw_test_syspll_enabled_pllctl0;
}

#define OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_READ32(address) \
    open_cfw_test_syspll_enabled_read32(address)

#include "../../components/apollo_main/core_overlay/pwrctrl_syspll_enabled.c"

void
open_cfw_test_syspll_enabled_reset(
    uint32_t pllctl0,
    uint32_t output
)
{
    open_cfw_test_syspll_enabled_pllctl0 = pllctl0;
    open_cfw_test_syspll_enabled_output = output;
    open_cfw_test_syspll_enabled_read_count = 0U;
    open_cfw_test_syspll_enabled_read_address = 0U;
}

uint32_t
open_cfw_test_syspll_enabled_call(void)
{
    return open_cfw_pwrctrl_syspll_enabled(
        (_Bool *)&open_cfw_test_syspll_enabled_output
    );
}
