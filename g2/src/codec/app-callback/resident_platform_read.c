/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10024810. The ten-entry jump table at 0x100249cc was
 * decoded from the authenticated SRAM image; direct native instructions
 * establish the MMIO read and output-store widths and order.
 */
#include <stdint.h>

/* Stock 0x10024810 (gx8002_platform_read) */
uint32_t gx8002_resident_platform_read_24810(uint32_t query, void *output)
{
    volatile const uint32_t *const analog =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0xa0000000);
    uint8_t *const bytes = output;
    switch (query) {
    case 0u:
        for (uint32_t i = 0u; i < 8u; ++i)
            ((uint16_t *)output)[i] = (uint16_t)analog[i + 1u];
        return 0u;
    case 1u: *(uint32_t *)output = analog[9]; return 0u;
    case 2u: *(uint32_t *)output = analog[10]; return 0u;
    case 3u: *(uint32_t *)output = analog[11] & 15u; return 0u;
    case 4u: *(uint32_t *)output = analog[13] & 15u; return 0u;
    case 5u: {
        volatile const uint32_t *const clock =
            (volatile const uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
        bytes[0] = (uint8_t)(clock[0x58u / 4u] & 1u);
        *(uint32_t *)(void *)(bytes + 4u) = clock[0x5cu / 4u];
        return 0u;
    }
    case 6u: *(uint32_t *)output = analog[12]; return 0u;
    case 7u: {
        uint32_t word = analog[0x40u / 4u];
        bytes[0] = (uint8_t)(word & 1u);
        bytes[1] = (uint8_t)analog[0x44u / 4u];
        word = analog[0x48u / 4u];
        bytes[2] = (uint8_t)(word & 15u);
        bytes[3] = (uint8_t)((word >> 4) & 15u);
        ((uint16_t *)(void *)bytes)[2] = (uint16_t)analog[0x4cu / 4u];
        bytes[6] = (uint8_t)analog[0x50u / 4u];
        bytes[7] = (uint8_t)analog[0x54u / 4u];
        return 0u;
    }
    case 8u: *(uint32_t *)output = analog[14]; return 0u;
    case 9u:
        *(uint32_t *)output = *(volatile const uint32_t *)(uintptr_t)
            UINT32_C(0x20027314);
        return 0u;
    default: return UINT32_MAX;
    }
}
