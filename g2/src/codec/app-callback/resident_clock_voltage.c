/* SPDX-License-Identifier: MIT
 * Native image-A SRAM analog voltage leaves 0x100246f0 and 0x10024710.
 * The 0x10024730 digital-voltage body reads an ambient stack byte and is
 * intentionally not substituted with guessed zero-initialized input.
 */
#include <stdint.h>

/* Stock 0x100246F0 (gx_analog_set_ldo_ana_voltage) */
uint32_t gx8002_resident_analog_ldo_voltage_246f0(uint32_t voltage)
{
    if (voltage == UINT32_MAX) return UINT32_MAX;
    volatile uint32_t *const analog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    uint32_t previous = analog[0x54u / 4u];
    analog[0x54u / 4u] = (uint8_t)((previous & 0xf0u) | voltage);
    return 0u;
}

/* Stock 0x10024710 (gx_analog_get_ldo_dig_ctrl) */
uint32_t gx8002_resident_analog_ldo_digital_state_24710(void)
{
    const volatile uint32_t *const analog =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    uint32_t status = (uint8_t)analog[0x58u / 4u];
    if ((status & 4u) == 0u) return 0u;
    return 1u + ((status >> 1) & 1u);
}
