#include <stddef.h>

unsigned int open_cfw_test_mcuctrl_info_sku_values[12];
unsigned int open_cfw_test_mcuctrl_info_sku_reads;
unsigned int open_cfw_test_mcuctrl_info_sku_addresses[12];
unsigned int open_cfw_test_mcuctrl_info_trim_calls;
unsigned int open_cfw_test_mcuctrl_info_trim_status;
unsigned int open_cfw_test_mcuctrl_info_trim_pointer_matches;
unsigned int open_cfw_test_mcuctrl_info_device_calls;
unsigned int open_cfw_test_mcuctrl_info_device_pointer_matches;
void *open_cfw_test_mcuctrl_info_expected_pointer;

static unsigned int
open_cfw_test_mcuctrl_info_read32(unsigned int address)
{
    unsigned int index = open_cfw_test_mcuctrl_info_sku_reads;

    if (index > 11U) {
        index = 11U;
    }
    open_cfw_test_mcuctrl_info_sku_addresses[index] = address;
    ++open_cfw_test_mcuctrl_info_sku_reads;
    return open_cfw_test_mcuctrl_info_sku_values[index];
}

static unsigned int open_cfw_test_mcuctrl_info_trim_version_get(
    void *feature
)
{
    unsigned int *words = (unsigned int *)feature;

    ++open_cfw_test_mcuctrl_info_trim_calls;
    open_cfw_test_mcuctrl_info_trim_pointer_matches =
        feature == open_cfw_test_mcuctrl_info_expected_pointer;
    words[3] = 0xA5A55A5AU;
    return open_cfw_test_mcuctrl_info_trim_status;
}

static void open_cfw_test_mcuctrl_info_device_info_get(void *device)
{
    unsigned int *words = (unsigned int *)device;

    ++open_cfw_test_mcuctrl_info_device_calls;
    open_cfw_test_mcuctrl_info_device_pointer_matches =
        device == open_cfw_test_mcuctrl_info_expected_pointer;
    words[0] = 0xD3D1C3D1U;
}

void open_cfw_test_mcuctrl_info_reset(void)
{
    unsigned int index;

    open_cfw_test_mcuctrl_info_sku_reads = 0U;
    open_cfw_test_mcuctrl_info_trim_calls = 0U;
    open_cfw_test_mcuctrl_info_trim_status = 0U;
    open_cfw_test_mcuctrl_info_trim_pointer_matches = 0U;
    open_cfw_test_mcuctrl_info_device_calls = 0U;
    open_cfw_test_mcuctrl_info_device_pointer_matches = 0U;
    open_cfw_test_mcuctrl_info_expected_pointer = (void *)0;
    for (index = 0U; index < 12U; ++index) {
        open_cfw_test_mcuctrl_info_sku_values[index] = 0U;
        open_cfw_test_mcuctrl_info_sku_addresses[index] = 0U;
    }
}

#define OPEN_CFW_MCUCTRL_INFO_READ32(address) \
    open_cfw_test_mcuctrl_info_read32(address)
#define OPEN_CFW_MCUCTRL_INFO_TRIM_VERSION_GET(feature) \
    open_cfw_test_mcuctrl_info_trim_version_get(feature)
#define OPEN_CFW_MCUCTRL_INFO_DEVICE_INFO_GET(device) \
    open_cfw_test_mcuctrl_info_device_info_get(device)

#include "../../components/apollo_main/core_overlay/mcuctrl_info.c"
