#include <stdint.h>

unsigned int open_cfw_test_mcuctrl_device_info_registers[14];
unsigned int open_cfw_test_mcuctrl_device_info_sku_sequence[8];
unsigned int open_cfw_test_mcuctrl_device_info_sku_count;
unsigned int open_cfw_test_mcuctrl_device_info_sku_index;
unsigned int open_cfw_test_mcuctrl_device_info_event_count;
unsigned int open_cfw_test_mcuctrl_device_info_event_kind[64];
unsigned int open_cfw_test_mcuctrl_device_info_event_address[64];
unsigned int open_cfw_test_mcuctrl_device_info_event_value[64];

static const unsigned int open_cfw_test_mcuctrl_device_info_addresses[14] = {
    0x40020000U,
    0x40020004U,
    0x40020008U,
    0x4002000CU,
    0x40020010U,
    0x40020014U,
    0xE00FEFE0U,
    0xE00FEFE4U,
    0xE00FEFE8U,
    0xE00FEFECU,
    0xE00FEFF0U,
    0xE00FEFF4U,
    0xE00FEFF8U,
    0xE00FEFFCU,
};

static void open_cfw_test_mcuctrl_device_info_event(
    unsigned int kind,
    unsigned int address,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_mcuctrl_device_info_event_count;

    open_cfw_test_mcuctrl_device_info_event_kind[index] = kind;
    open_cfw_test_mcuctrl_device_info_event_address[index] = address;
    open_cfw_test_mcuctrl_device_info_event_value[index] = value;
    ++open_cfw_test_mcuctrl_device_info_event_count;
}

static unsigned int
open_cfw_test_mcuctrl_device_info_read32(unsigned int address)
{
    unsigned int index;
    unsigned int value = 0U;

    for (index = 0U; index < 14U; ++index) {
        if (open_cfw_test_mcuctrl_device_info_addresses[index] == address) {
            value = open_cfw_test_mcuctrl_device_info_registers[index];
            break;
        }
    }

    if (address == 0x40020014U) {
        index = open_cfw_test_mcuctrl_device_info_sku_index;
        if (index < open_cfw_test_mcuctrl_device_info_sku_count) {
            value = open_cfw_test_mcuctrl_device_info_sku_sequence[index];
        }
        ++open_cfw_test_mcuctrl_device_info_sku_index;
    }

    open_cfw_test_mcuctrl_device_info_event(1U, address, value);
    return value;
}

static void
open_cfw_test_mcuctrl_device_info_delay_us(unsigned int microseconds)
{
    open_cfw_test_mcuctrl_device_info_event(2U, 0U, microseconds);
}

#define OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(address) \
    open_cfw_test_mcuctrl_device_info_read32(address)
#define OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(microseconds) \
    open_cfw_test_mcuctrl_device_info_delay_us(microseconds)

#include "../../components/apollo_main/core_overlay/mcuctrl_device_info.c"

void open_cfw_test_mcuctrl_device_info_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 14U; ++index) {
        open_cfw_test_mcuctrl_device_info_registers[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_mcuctrl_device_info_sku_sequence[index] = 0U;
    }
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_mcuctrl_device_info_event_kind[index] = 0U;
        open_cfw_test_mcuctrl_device_info_event_address[index] = 0U;
        open_cfw_test_mcuctrl_device_info_event_value[index] = 0U;
    }
    open_cfw_test_mcuctrl_device_info_sku_count = 0U;
    open_cfw_test_mcuctrl_device_info_sku_index = 0U;
    open_cfw_test_mcuctrl_device_info_event_count = 0U;
}
