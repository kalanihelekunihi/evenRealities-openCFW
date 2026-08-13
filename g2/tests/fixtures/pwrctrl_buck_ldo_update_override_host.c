#include <stdint.h>

uint32_t open_cfw_test_buck_ldo_update_register;
uint32_t open_cfw_test_buck_ldo_update_read_count;
uint32_t open_cfw_test_buck_ldo_update_write_count;
uint32_t open_cfw_test_buck_ldo_update_read_addresses[3];
uint32_t open_cfw_test_buck_ldo_update_write_addresses[3];
uint32_t open_cfw_test_buck_ldo_update_write_values[3];

static uint32_t
open_cfw_test_buck_ldo_update_read(uint32_t address)
{
    if (open_cfw_test_buck_ldo_update_read_count < 3U) {
        open_cfw_test_buck_ldo_update_read_addresses[
            open_cfw_test_buck_ldo_update_read_count
        ] = address;
    }
    ++open_cfw_test_buck_ldo_update_read_count;
    return open_cfw_test_buck_ldo_update_register;
}

static void
open_cfw_test_buck_ldo_update_write(uint32_t address, uint32_t value)
{
    if (open_cfw_test_buck_ldo_update_write_count < 3U) {
        open_cfw_test_buck_ldo_update_write_addresses[
            open_cfw_test_buck_ldo_update_write_count
        ] = address;
        open_cfw_test_buck_ldo_update_write_values[
            open_cfw_test_buck_ldo_update_write_count
        ] = value;
    }
    ++open_cfw_test_buck_ldo_update_write_count;
    open_cfw_test_buck_ldo_update_register = value;
}

#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_READ32(address) \
    open_cfw_test_buck_ldo_update_read(address)
#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_WRITE32(address, value) \
    open_cfw_test_buck_ldo_update_write((address), (value))

#include "../../components/apollo_main/core_overlay/pwrctrl_buck_ldo_update_override.c"

void open_cfw_test_buck_ldo_update_reset(uint32_t value)
{
    unsigned int index;

    open_cfw_test_buck_ldo_update_register = value;
    open_cfw_test_buck_ldo_update_read_count = 0U;
    open_cfw_test_buck_ldo_update_write_count = 0U;
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_buck_ldo_update_read_addresses[index] = 0U;
        open_cfw_test_buck_ldo_update_write_addresses[index] = 0U;
        open_cfw_test_buck_ldo_update_write_values[index] = 0U;
    }
}
