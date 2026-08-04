#include <stdint.h>

uint32_t open_cfw_test_cpdlp_get_state;
uint32_t open_cfw_test_cpdlp_get_read_count;
uint32_t open_cfw_test_cpdlp_get_read_address;

static uint32_t open_cfw_test_cpdlp_get_read32(uint32_t address)
{
    open_cfw_test_cpdlp_get_read_address = address;
    ++open_cfw_test_cpdlp_get_read_count;
    return open_cfw_test_cpdlp_get_state;
}

#define OPEN_CFW_PWRCTRL_CPDLP_GET_READ32(address) \
    open_cfw_test_cpdlp_get_read32(address)

#include "../../components/apollo_main/core_overlay/pwrctrl_cpdlp_get.c"

void
open_cfw_test_cpdlp_get_reset(uint32_t state)
{
    open_cfw_test_cpdlp_get_state = state;
    open_cfw_test_cpdlp_get_read_count = 0U;
    open_cfw_test_cpdlp_get_read_address = 0U;
}
