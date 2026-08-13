#include <stdint.h>

uint32_t open_cfw_test_buck_ldo_register;
uint32_t open_cfw_test_buck_ldo_read_count;
uint32_t open_cfw_test_buck_ldo_write_count;
uint32_t open_cfw_test_buck_ldo_read_addresses[10];
uint32_t open_cfw_test_buck_ldo_write_addresses[10];
uint32_t open_cfw_test_buck_ldo_write_values[10];

static uint32_t
open_cfw_test_buck_ldo_read(uint32_t address)
{
    if (open_cfw_test_buck_ldo_read_count < 10U) {
        open_cfw_test_buck_ldo_read_addresses[
            open_cfw_test_buck_ldo_read_count
        ] = address;
    }
    ++open_cfw_test_buck_ldo_read_count;
    return open_cfw_test_buck_ldo_register;
}

static void
open_cfw_test_buck_ldo_write(uint32_t address, uint32_t value)
{
    if (open_cfw_test_buck_ldo_write_count < 10U) {
        open_cfw_test_buck_ldo_write_addresses[
            open_cfw_test_buck_ldo_write_count
        ] = address;
        open_cfw_test_buck_ldo_write_values[
            open_cfw_test_buck_ldo_write_count
        ] = value;
    }
    ++open_cfw_test_buck_ldo_write_count;
    open_cfw_test_buck_ldo_register = value;
}

#define OPEN_CFW_PWRCTRL_BUCK_LDO_READ32(address) \
    open_cfw_test_buck_ldo_read(address)
#define OPEN_CFW_PWRCTRL_BUCK_LDO_WRITE32(address, value) \
    open_cfw_test_buck_ldo_write((address), (value))

#include "../../components/apollo_main/core_overlay/pwrctrl_buck_ldo_override_init.c"

void open_cfw_test_buck_ldo_reset(uint32_t value)
{
    unsigned int index;

    open_cfw_test_buck_ldo_register = value;
    open_cfw_test_buck_ldo_read_count = 0U;
    open_cfw_test_buck_ldo_write_count = 0U;
    for (index = 0U; index < 10U; ++index) {
        open_cfw_test_buck_ldo_read_addresses[index] = 0U;
        open_cfw_test_buck_ldo_write_addresses[index] = 0U;
        open_cfw_test_buck_ldo_write_values[index] = 0U;
    }
}
