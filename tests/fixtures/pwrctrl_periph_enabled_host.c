#include <stddef.h>
#include <stdint.h>

unsigned int open_cfw_test_enabled_descriptor_result;
unsigned int open_cfw_test_enabled_descriptor_calls;
unsigned int open_cfw_test_enabled_last_peripheral;
unsigned int open_cfw_test_enabled_status_address;
unsigned int open_cfw_test_enabled_status_mask;
unsigned int open_cfw_test_enabled_status_register;
unsigned int open_cfw_test_enabled_read_calls;

static unsigned int
open_cfw_test_enabled_read(unsigned int address)
{
    ++open_cfw_test_enabled_read_calls;
    return address == open_cfw_test_enabled_status_address
        ? open_cfw_test_enabled_status_register
        : 0U;
}

static unsigned int open_cfw_test_enabled_descriptor_get(
    void *,
    unsigned int
);

#define OPEN_CFW_PWRCTRL_ENABLED_READ(address) \
    open_cfw_test_enabled_read(address)
#define OPEN_CFW_PWRCTRL_ENABLED_DESCRIPTOR_GET(descriptor, peripheral) \
    open_cfw_test_enabled_descriptor_get((descriptor), (peripheral))

#include "../../components/apollo_main/core_overlay/pwrctrl_periph_enabled.c"

static unsigned int
open_cfw_test_enabled_descriptor_get(
    void *output,
    unsigned int peripheral
)
{
    open_cfw_pwrctrl_enabled_descriptor *descriptor =
        (open_cfw_pwrctrl_enabled_descriptor *)output;

    ++open_cfw_test_enabled_descriptor_calls;
    open_cfw_test_enabled_last_peripheral = peripheral;
    if (open_cfw_test_enabled_descriptor_result != 0U) {
        return open_cfw_test_enabled_descriptor_result;
    }
    descriptor->power_enable_register =
        0x1000U;
    descriptor->peripheral_enable_mask =
        0x20U;
    descriptor->power_status_register =
        open_cfw_test_enabled_status_address;
    descriptor->peripheral_status_mask =
        open_cfw_test_enabled_status_mask;
    return 0U;
}

void open_cfw_test_enabled_reset(void)
{
    open_cfw_test_enabled_descriptor_result = 0U;
    open_cfw_test_enabled_descriptor_calls = 0U;
    open_cfw_test_enabled_last_peripheral = 0U;
    open_cfw_test_enabled_status_address = 0x1004U;
    open_cfw_test_enabled_status_mask = 0x200U;
    open_cfw_test_enabled_status_register = 0U;
    open_cfw_test_enabled_read_calls = 0U;
}
