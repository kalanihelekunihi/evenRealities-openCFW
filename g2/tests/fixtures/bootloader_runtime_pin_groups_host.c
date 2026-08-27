#include <stdint.h>

#define OPEN_CFW_PIN_GROUPS_HOST 1

static uint32_t fixture_pins[20];
static uint32_t fixture_values[20];
static uint32_t fixture_count;

uint32_t open_cfw_pin_groups_host_config(uint32_t offset)
{
    return 0xA5000000U | offset;
}

uint32_t open_cfw_pin_groups_host_configure(uint32_t pin, uint32_t value)
{
    fixture_pins[fixture_count] = pin;
    fixture_values[fixture_count] = value;
    ++fixture_count;
    return 0U;
}

#include "../../components/bootloader/core_overlay/runtime_pin_groups_41fadc.c"

static uint32_t run_case(
    uint32_t bank,
    uint32_t subtype,
    const uint32_t *pins,
    const uint32_t *offsets,
    uint32_t count)
{
    uint32_t index;
    fixture_count = 0U;
    open_cfw_bootloader_pin_groups_41fadc(bank, subtype);
    if (fixture_count != count) {
        return 0U;
    }
    for (index = 0U; index < count; ++index) {
        if (fixture_pins[index] != pins[index] ||
            fixture_values[index] != (0xA5000000U | offsets[index])) {
            return 0U;
        }
    }
    return 1U;
}

uint32_t open_cfw_test_pin_groups(void)
{
    static const uint32_t bank_zero_ten_pins[19] = {
        0x25U, 0x26U, 0x27U, 0x28U, 0x29U, 0x2AU, 0x2BU, 0x2CU, 0x2DU,
        0x44U, 0x45U, 0x46U, 0x47U, 0x42U, 0x43U,
        0xC7U, 0x40U, 0x41U, 0x48U
    };
    static const uint32_t bank_zero_ten_offsets[19] = {
        0x28U, 0x2CU, 0x30U, 0x34U, 0x38U, 0x3CU, 0x40U, 0x44U, 0x48U,
        0x14U, 0x18U, 0x1CU, 0x20U, 0x0CU, 0x10U,
        0x00U, 0x04U, 0x08U, 0x24U
    };
    static const uint32_t bank_one_six_pins[11] = {
        0x63U, 0x64U, 0x65U, 0x66U, 0x61U, 0x62U,
        0x31U, 0x5FU, 0x60U, 0x67U, 0x68U
    };
    static const uint32_t bank_one_six_offsets[11] = {
        0x60U, 0x64U, 0x68U, 0x6CU, 0x58U, 0x5CU,
        0x4CU, 0x50U, 0x54U, 0x70U, 0x74U
    };
    static const uint32_t bank_zero_four_pins[6] = {
        0x42U, 0x43U, 0xC7U, 0x40U, 0x41U, 0x48U
    };
    static const uint32_t bank_zero_four_offsets[6] = {
        0x0CU, 0x10U, 0x00U, 0x04U, 0x08U, 0x24U
    };

    if (!run_case(0U, 10U, bank_zero_ten_pins, bank_zero_ten_offsets, 19U) ||
        !run_case(1U, 6U, bank_one_six_pins, bank_one_six_offsets, 11U) ||
        !run_case(0U, 0x104U, bank_zero_four_pins,
            bank_zero_four_offsets, 6U)) {
        return 0U;
    }
    fixture_count = 0U;
    open_cfw_bootloader_pin_groups_41fadc(0U, 1U);
    open_cfw_bootloader_pin_groups_41fadc(1U, 25U);
    open_cfw_bootloader_pin_groups_41fadc(2U, 0U);
    open_cfw_bootloader_pin_groups_41fadc(3U, 0U);
    open_cfw_bootloader_pin_groups_41fadc(9U, 10U);
    return fixture_count == 0U;
}
