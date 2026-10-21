#include <stdint.h>

/* Stock 0x00590a24..0x00590b6b. Configuration and descriptor are
 * caller-owned objects. The native body reads handle+4 before checking
 * the handle; callers must pass a mapped handle. */
enum { I2S_BASE = 0x40208000u, I2S_MARKER = 0x01125125u };

uint32_t g2_codec_i2s_dma_configure(void *handle, const void *config,
                                     const void *descriptor) {
    uint32_t *const h = (uint32_t *)handle;
    uint32_t const instance = h[1];
    if (handle == 0 || (h[0] & 0x01ffffffu) != I2S_MARKER)
        return 2u;
    const uint32_t *const d = (const uint32_t *)descriptor;
    volatile uint32_t *const mmio = (volatile uint32_t *)(uintptr_t)
        (I2S_BASE + (instance << 12));
    const uint8_t *const cfg = (const uint8_t *)config;
    h[0x3cu / 4u] = d[0];
    h[0x4cu / 4u] = h[0x3cu / 4u];
    h[0x40u / 4u] = d[1];
    h[0x44u / 4u] = d[3];
    h[0x50u / 4u] = h[0x44u / 4u];
    h[0x48u / 4u] = d[4];
    h[0x54u / 4u] = d[2] << 2;
    h[0x58u / 4u] = d[5] << 2;
    *(uint32_t *)((uintptr_t)config + 0x24u) = (uint32_t)(uintptr_t)descriptor;
    mmio[0x308u / 4u] = 31u;
    mmio[0x4cu / 4u] = 0u;
    mmio[0x200u / 4u] |= 0x01000000u;
    switch (cfg[1]) {
    case 0u:
        mmio[0x224u / 4u] = h[0x3cu / 4u];
        mmio[0x220u / 4u] = h[0x54u / 4u] >> 2;
        mmio[0x21cu / 4u] = 1u;
        mmio[0x4cu / 4u] = 16u;
        mmio[0x300u / 4u] = 16u;
        break;
    case 1u:
        mmio[0x22cu / 4u] = h[0x44u / 4u];
        mmio[0x228u / 4u] = h[0x58u / 4u] >> 2;
        mmio[0x21cu / 4u] = 2u;
        mmio[0x4cu / 4u] = 32u;
        mmio[0x300u / 4u] = 8u;
        break;
    case 2u:
        mmio[0x22cu / 4u] = h[0x44u / 4u];
        mmio[0x228u / 4u] = h[0x58u / 4u] >> 2;
        mmio[0x224u / 4u] = h[0x3cu / 4u];
        mmio[0x220u / 4u] = h[0x54u / 4u] >> 2;
        mmio[0x21cu / 4u] = 3u;
        mmio[0x4cu / 4u] = 48u;
        mmio[0x300u / 4u] = 24u;
        break;
    default:
        break;
    }
    mmio[0x200u / 4u] |= 2u;
    mmio[0x200u / 4u] |= 32u;
    return 0u;
}
