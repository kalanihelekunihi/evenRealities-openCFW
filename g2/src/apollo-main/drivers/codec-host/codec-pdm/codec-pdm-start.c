#include <stdint.h>

/* Native 0x59233c: choose the widest supported descriptor element size. */
uint32_t g2_pdm_descriptor_stride(uint32_t bytes) {
    for (uint32_t stride = 24u; stride >= 16u; stride -= 4u) {
        if (bytes % stride == 0u)
            return stride;
    }
    return 0u;
}

extern void stock_delay_us(uint32_t microseconds); /* 0x4807a0 */

/* Native 0x59235e..0x59243d. The descriptor is three native words. */
uint32_t g2_pdm_start(void *handle, const void *descriptor) {
    uint32_t *const h = (uint32_t *)handle;
    const uint32_t *const d = (const uint32_t *)descriptor;
    if (h == 0 || (h[0] & 0x01ffffffu) != 0x01f956e2u)
        return 2u;

    const uint32_t instance = h[2];
    h[3] = d[0];
    h[5] = h[3];
    h[4] = d[1];
    h[6] = d[2];
    const uint32_t stride = g2_pdm_descriptor_stride(d[2]);
    if (stride == 0u)
        return 0x08000000u;

    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)
        (0x40201000u + (instance << 12));
    reg[0x1cu / 4u] = stride;
    reg[0x140u / 4u] |= 1u;
    reg[0x158u / 4u] = 0u;
    ((uint8_t *)h)[30] = 0u;
    reg[0x148u / 4u] = 1u;
    reg[0x148u / 4u] |= 0x800u;
    reg[0x160u / 4u] = h[3];
    reg[0x164u / 4u] = h[6];
    reg[0x168u / 4u] = 1u;
    if (h[4] == UINT32_MAX)
        return 0u;

    stock_delay_us(10u);
    if (reg[0x168u / 4u] != 0u)
        return 9u;
    h[5] = h[4];
    reg[0x160u / 4u] = h[4];
    reg[0x164u / 4u] = h[6];
    reg[0x168u / 4u] = 1u;
    return 0u;
}
