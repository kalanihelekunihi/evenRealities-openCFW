#include <stdint.h>

unsigned int open_cfw_test_disable_mask_descriptor_result;
unsigned int open_cfw_test_disable_mask_enable_address;
unsigned int open_cfw_test_disable_mask_enable_mask;
unsigned int open_cfw_test_disable_mask_status_address;
unsigned int open_cfw_test_disable_mask_status_mask;
unsigned int open_cfw_test_disable_mask_enable_value;
unsigned int open_cfw_test_disable_mask_descriptor_peripheral;
unsigned int open_cfw_test_disable_mask_read_count;

static unsigned int
open_cfw_test_disable_mask_descriptor_get(void *, unsigned int);
static unsigned int open_cfw_test_disable_mask_read(unsigned int);

#define OPEN_CFW_PWRCTRL_DISABLE_MASK_DESCRIPTOR_GET(descriptor, peripheral) \
    open_cfw_test_disable_mask_descriptor_get((descriptor), (peripheral))
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_READ(address) \
    open_cfw_test_disable_mask_read(address)

#include "../../components/apollo_main/core_overlay/pwrctrl_periph_disable_mask_check.c"

static unsigned int
open_cfw_test_disable_mask_descriptor_get(
    void *output,
    unsigned int peripheral
)
{
    open_cfw_pwrctrl_disable_mask_descriptor *descriptor =
        (open_cfw_pwrctrl_disable_mask_descriptor *)output;

    open_cfw_test_disable_mask_descriptor_peripheral = peripheral;
    if (open_cfw_test_disable_mask_descriptor_result != 0U) {
        return open_cfw_test_disable_mask_descriptor_result;
    }
    descriptor->power_enable_register =
        open_cfw_test_disable_mask_enable_address;
    descriptor->peripheral_enable_mask =
        open_cfw_test_disable_mask_enable_mask;
    descriptor->power_status_register =
        open_cfw_test_disable_mask_status_address;
    descriptor->peripheral_status_mask =
        open_cfw_test_disable_mask_status_mask;
    return 0U;
}

static unsigned int
open_cfw_test_disable_mask_read(unsigned int address)
{
    ++open_cfw_test_disable_mask_read_count;
    return address == open_cfw_test_disable_mask_enable_address
        ? open_cfw_test_disable_mask_enable_value
        : 0U;
}

void open_cfw_test_disable_mask_reset(void)
{
    open_cfw_test_disable_mask_descriptor_result = 0U;
    open_cfw_test_disable_mask_enable_address = 0x1000U;
    open_cfw_test_disable_mask_enable_mask = 1U;
    open_cfw_test_disable_mask_status_address = 0x1004U;
    open_cfw_test_disable_mask_status_mask = 0x30000001U;
    open_cfw_test_disable_mask_enable_value = 0U;
    open_cfw_test_disable_mask_descriptor_peripheral = 0U;
    open_cfw_test_disable_mask_read_count = 0U;
}
