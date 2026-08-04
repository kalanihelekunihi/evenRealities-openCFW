#include <stdint.h>

uint32_t open_cfw_test_cpdlp_cache_control;
uint32_t open_cfw_test_cpdlp_state;
uint32_t open_cfw_test_cpdlp_read_count;
uint32_t open_cfw_test_cpdlp_write_count;
uint32_t open_cfw_test_cpdlp_read_address;
uint32_t open_cfw_test_cpdlp_write_address;
uint32_t open_cfw_test_cpdlp_write_value;
uint32_t open_cfw_test_cpdlp_operations[2];
uint32_t open_cfw_test_cpdlp_operation_count;

static uint32_t open_cfw_test_cpdlp_read32(uint32_t address)
{
    open_cfw_test_cpdlp_read_address = address;
    ++open_cfw_test_cpdlp_read_count;
    open_cfw_test_cpdlp_operations[
        open_cfw_test_cpdlp_operation_count++
    ] = 1U;
    return open_cfw_test_cpdlp_cache_control;
}

static void
open_cfw_test_cpdlp_write32(uint32_t address, uint32_t value)
{
    open_cfw_test_cpdlp_write_address = address;
    open_cfw_test_cpdlp_write_value = value;
    open_cfw_test_cpdlp_state = value;
    ++open_cfw_test_cpdlp_write_count;
    open_cfw_test_cpdlp_operations[
        open_cfw_test_cpdlp_operation_count++
    ] = 2U;
}

#define OPEN_CFW_PWRCTRL_CPDLP_READ32(address) \
    open_cfw_test_cpdlp_read32(address)
#define OPEN_CFW_PWRCTRL_CPDLP_WRITE32(address, value) \
    open_cfw_test_cpdlp_write32((address), (value))

#include "../../components/apollo_main/core_overlay/pwrctrl_cpdlp_config.c"

void
open_cfw_test_cpdlp_reset(uint32_t cache_control, uint32_t state)
{
    open_cfw_test_cpdlp_cache_control = cache_control;
    open_cfw_test_cpdlp_state = state;
    open_cfw_test_cpdlp_read_count = 0U;
    open_cfw_test_cpdlp_write_count = 0U;
    open_cfw_test_cpdlp_read_address = 0U;
    open_cfw_test_cpdlp_write_address = 0U;
    open_cfw_test_cpdlp_write_value = 0U;
    open_cfw_test_cpdlp_operations[0] = 0U;
    open_cfw_test_cpdlp_operations[1] = 0U;
    open_cfw_test_cpdlp_operation_count = 0U;
}
