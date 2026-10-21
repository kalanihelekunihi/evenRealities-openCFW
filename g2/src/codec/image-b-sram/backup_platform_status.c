/* SPDX-License-Identifier: MIT
 * Image-B SoC status 0x10003fb8, retention 0x10003ffc, and unseeded
 * gated status read 0x1000401c. Native volatile read order is retained.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enabled);

uint32_t gx8002_image_b_platform_status_10003fb8(void)
{
    uint32_t status = *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0000034);
    if (status & 1u) return 2u;
    if (status & 4u) return 3u;
    if (status & 8u) return 5u;
    if (status & 2u) return 4u;
    return *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa001002c) & 1u;
}

uint32_t gx8002_image_b_preserve_memory_10003ffc(void)
{
    uint32_t status = gx8002_image_b_platform_status_10003fb8();
    if (status - 2u < 4u) {
        volatile uint32_t *retention =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010058);
        uint32_t enabled = retention[0] & 1u;
        (void)retention[1];
        return enabled;
    }
    return 0u;
}

uint32_t gx8002_image_b_gated_status_1000401c(void)
{
    gx8002_image_b_platform_gate_10003be8(9u, 1u);
    return *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010030) & 1u;
}
