/* SPDX-License-Identifier: MIT
 * CASE 0x0800856c. The two timing tables at 0x0800d398 and 0x0800d3a0
 * remain product data contracts; this source expresses the complete body.
 */
#include <stdint.h>

extern const uint8_t case_boot_sensor_divisor_table[8]; /* 0x0800d398 */
extern const uint8_t case_boot_sensor_rate_table[8];    /* 0x0800d3a0 */
extern uint32_t case_policy_sensor_divide(uint32_t, uint32_t); /* 0x08000160 */

static uint32_t rd32(uint32_t address)
{
    return *(volatile uint32_t *)(uintptr_t)address;
}

static void wr16(uint32_t address, uint16_t value)
{
    *(volatile uint16_t *)(uintptr_t)address = value;
}

void case_boot_sensor_commit(uint32_t descriptor)
{
    uint32_t settings = descriptor + 64u;
    if (rd32(descriptor + 100u) == 0u) {
        wr16(settings + 42u, 1u);
        wr16(settings + 40u, 1u);
        return;
    }

    uint32_t control = rd32(rd32(descriptor) + 8u);
    uint32_t first = control >> 29;
    uint32_t second = (control >> 25) & 7u;
    wr16(settings + 42u, (uint16_t)case_policy_sensor_divide(
        (uint32_t)case_boot_sensor_divisor_table[first] << 3,
        case_boot_sensor_rate_table[first]));
    wr16(settings + 40u, (uint16_t)case_policy_sensor_divide(
        (uint32_t)case_boot_sensor_divisor_table[second] << 3,
        case_boot_sensor_rate_table[second]));
}
