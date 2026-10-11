#include <stdint.h>

extern void stock_delay_us(uint32_t microseconds); /* 0x4807a0 */

static uint32_t field(uint32_t prior, uint32_t value,
                      uint32_t shift, uint32_t width) {
    uint32_t const mask = ((1u << width) - 1u) << shift;
    return (prior & ~mask) | ((value << shift) & mask);
}

/* Native 0x5920cc..0x59222f. Keep the original ordered MMIO writes. */
uint32_t g2_pdm_configure(void *handle, const void *config) {
    uint32_t *const h = (uint32_t *)handle;
    const uint8_t *const c = (const uint8_t *)config;
    if (h == 0 || (h[0] & 0x01ffffffu) != 0x01f956e2u)
        return 2u;

    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)
        (0x40201000u + (h[2] << 12));
    reg[1] = field(reg[1], c[27], 0u, 1u);
    reg[1] = field(reg[1], c[26], 1u, 1u);
    reg[1] = field(reg[1], c[25], 2u, 3u);
    reg[1] = field(reg[1], c[16], 5u, 4u);
    reg[1] = field(reg[1], c[12], 9u, 1u);
    reg[1] = field(reg[1], c[1], 10u, 4u);
    reg[1] = field(reg[1], c[8], 14u, 7u);
    reg[1] = field(reg[1], c[2], 21u, 5u);
    reg[1] = field(reg[1], c[3], 26u, 5u);
    reg[2] = (reg[2] & ~3u) | (c[23] & 3u);
    reg[2] = field(reg[2], c[0], 2u, 2u);
    reg[2] = field(reg[2], c[24], 4u, 3u);
    reg[2] = field(reg[2], c[4], 7u, 1u);
    reg[0] &= ~1u;
    reg[0] = field(reg[0], c[22], 5u, 1u);
    reg[0] |= 0x80u;
    *(uint16_t *)((uint8_t *)h + 28u) =
        (uint16_t)c[20] | ((uint16_t)c[21] << 8);
    reg[0] &= ~0x10u;
    stock_delay_us(100u);
    reg[0] |= 0x10u;
    return 0u;
}
