/* SPDX-License-Identifier: MIT
 * Native platform configuration dispatch, stock 0x10025d74 and its ten
 * authenticated jump-table targets at 0x100249a4. Caller supplies data.
 */
#include <stdint.h>

/* Stock 0x10025D74 (gx8002_platform_config) */
uint32_t gx8002_resident_platform_config_25d74(
    uint32_t module, uint32_t *input)
{
    volatile uint32_t *const clock =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0000000);
    switch (module) {
    case 0: {
        const uint16_t *parts = (const uint16_t *)input;
        for (uint32_t i = 0; i < 8u; ++i) clock[i + 1u] = parts[i];
        return 0u;
    }
    case 1: clock[0x24u / 4u] = input[0]; return 0u;
    case 2: clock[0x28u / 4u] = input[0]; return 0u;
    case 3: clock[0x2cu / 4u] = input[0]; return 0u;
    case 4: clock[0x34u / 4u] = input[0]; return 0u;
    case 5: {
        const uint8_t *bytes = (const uint8_t *)input;
        volatile uint32_t *const pmu =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
        pmu[0x58u / 4u] = bytes[0] & 1u;
        pmu[0x5cu / 4u] = input[1];
        return 0u;
    }
    case 6: return UINT32_MAX;
    case 7: {
        const uint8_t *bytes = (const uint8_t *)input;
        clock[0x4cu / 4u] = ((const uint16_t *)(const void *)
                               (bytes + 4))[0];
        clock[0x48u / 4u] = ((uint32_t)bytes[3] << 4) | bytes[2];
        clock[0x44u / 4u] = bytes[1] != 0u;
        clock[0x40u / 4u] = bytes[0] != 0u;
        return 0u;
    }
    case 8: clock[0x38u / 4u] = input[0]; return 0u;
    case 9: {
        uint32_t value = input[0] & 1u;
        clock[0x3cu / 4u] = value;
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20027314) = value;
        return 0u;
    }
    default: return UINT32_MAX;
    }
}
