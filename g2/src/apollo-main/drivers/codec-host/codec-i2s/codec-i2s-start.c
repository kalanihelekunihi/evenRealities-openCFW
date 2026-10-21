#include <stdint.h>

/* Stock 0x005904ce..0x0059063d (368 bytes). The peripheral base and
 * handle magic are authenticated instruction literals. */
int32_t g2_codec_i2s_start(void *handle, const void *config) {
    uint32_t *const state = (uint32_t *)handle;
    const uint8_t *const options = (const uint8_t *)config;
    if (state == 0 || (state[0] & 0x01ffffffu) != 0x01125125u)
        return 2;

    volatile uint8_t *const base = (volatile uint8_t *)(uintptr_t)
        (0x40208000u + state[1] * 0x1000u);
    uint32_t status = *(volatile uint32_t *)(base + 0x28u);
    if ((status & 0x1fffffffu) != 0u)
        return 1;

    uint8_t mode = options[1];
    volatile uint32_t *const control = (volatile uint32_t *)(base + 0x200u);
    volatile uint32_t *const direction = (volatile uint32_t *)(base + 0x48u);
    if (mode == 0u) {
        *control |= 1u;
        *direction = 0x10u;
    } else if (mode == 1u) {
        *control |= 0x10u;
        *direction = 1u;
    } else if (mode == 2u) {
        *control |= 1u;
        *control |= 0x10u;
        *direction = 0x11u;
    }

    if (mode == 0u && state[0x10] != 0xffffffffu) {
        state[0x13] = state[0x10];
        *(volatile uint32_t *)(base + 0x224u) = state[0x13];
        *(volatile uint32_t *)(base + 0x220u) = state[0x15] >> 2;
        *(volatile uint32_t *)(base + 0x21cu) = 1u;
    } else if (mode == 1u && state[0x12] != 0xffffffffu) {
        state[0x14] = state[0x12];
        *(volatile uint32_t *)(base + 0x22cu) = state[0x14];
        *(volatile uint32_t *)(base + 0x228u) = state[0x16] >> 2;
        *(volatile uint32_t *)(base + 0x21cu) = 2u;
    } else if (mode == 2u && state[0x12] != 0xffffffffu &&
               state[0x10] != 0xffffffffu) {
        state[0x14] = state[0x12];
        *(volatile uint32_t *)(base + 0x22cu) = state[0x14];
        *(volatile uint32_t *)(base + 0x228u) = state[0x16] >> 2;
        state[0x13] = state[0x10];
        *(volatile uint32_t *)(base + 0x224u) = state[0x13];
        *(volatile uint32_t *)(base + 0x220u) = state[0x15] >> 2;
        *(volatile uint32_t *)(base + 0x21cu) = 3u;
    }
    return 0;
}
