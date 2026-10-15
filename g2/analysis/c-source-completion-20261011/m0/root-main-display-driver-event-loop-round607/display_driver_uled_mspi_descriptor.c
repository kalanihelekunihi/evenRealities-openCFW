/* Apollo S200 MSPI transfer descriptor encoder at 0x4bfa3c. */
#include <stdint.h>

extern uint32_t g2_main_mspi_queue_flags_4bfa10(uint32_t, uint32_t);

static uint32_t word(const uint8_t *p, uint32_t offset) {
    return *(const uint32_t *)(const void *)(p + offset);
}

uint32_t display_driver_uled_mspi_descriptor_4bfa3c(
    uint32_t handle, uint32_t kind, uint32_t descriptor,
    const void *transfer) {
    const uint8_t *const h = (const uint8_t *)(uintptr_t)handle;
    const uint8_t *const t = (const uint8_t *)transfer;
    uint32_t *const d = (uint32_t *)(uintptr_t)descriptor;
    const uint32_t module = word(h, 4);
    const uint32_t base = 0x40060000u + module * 0x1000u;
    if ((uint8_t)kind == 0u) {
        if (word(t, 0) > 0xffffu) return 5u;
        if (t[0x12] != 0u) return 7u;
        d[0] = base + 8u;
        d[1] = word(t, 8);
        d[2] = base + 0xcu;
        d[3] = (uint32_t)*(const uint16_t *)(const void *)(t + 0xe);
        d[4] = base;
        d[5] = ((uint32_t)t[5] << 11) | (word(t, 0) << 16) |
               ((uint32_t)t[4] << 9) | ((uint32_t)(t[6] & 1u) << 7) |
               ((uint32_t)t[12] << 6) | ((uint32_t)t[7] << 5) |
               ((uint32_t)t[16] << 10) | ((uint32_t)h[13] << 8) |
               ((uint32_t)t[0x11] << 12) | 1u;
        return 0u;
    }
    if ((uint8_t)kind == 1u) {
        if (word(t, 4) > 0xffffffu) return 5u;
        if (word(h, 0x838) != 0u && word(t, 16) != 0u) return 7u;
        d[12] = base + 0x100u;
        d[13] = 0u;
        d[4] = base + 0x108u;
        d[5] = word(t, 12);
        d[6] = base + 0x10cu;
        d[7] = word(t, 8);
        d[8] = base + 0x110u;
        d[9] = word(t, 4);
        d[10] = base + 0x100u;
        d[11] = ((uint32_t)(t[0] & 3u) << 4) |
                ((uint32_t)(t[1] & 1u) << 2) | 3u;
        d[2] = base + 0x2b8u;
        d[0] = d[2];
        d[1] = g2_main_mspi_queue_flags_4bfa10(handle, word(t, 16));
        d[3] = 0x4000u;
        d[15] = word(t, 20);
        d[14] = base + 0x2b4u;
    }
    return 0u;
}
