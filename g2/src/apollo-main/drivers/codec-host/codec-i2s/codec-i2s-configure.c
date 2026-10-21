#include <stdint.h>

/* Stock 0x00590104..0x005904cd. The source table is the six-word
 * table referenced by the native literal at 0x590cf0 (0x774b94). */
static const uint32_t slot_width[6] = { 8u, 0u, 16u, 0u, 24u, 32u };
extern void stock_delay_us(uint32_t us);              /* native 0x4807a0 */
extern uint32_t audio_i2s_clock_source(uint32_t src); /* native 0x58fd1c */
/* Authenticated silicon revision register from literal 0x590d30. */
static volatile const uint32_t *const chip_revision =
    (volatile const uint32_t *)(uintptr_t)0x4002000cu;

static uint32_t word(const uint8_t *p, uint32_t offset) {
    uint32_t v;
    __builtin_memcpy(&v, p + offset, sizeof v);
    return v;
}
static double number(const uint8_t *p, uint32_t offset) {
    double v;
    __builtin_memcpy(&v, p + offset, sizeof v);
    return v;
}
static void *pointer(const uint8_t *p, uint32_t offset) {
    return (void *)(uintptr_t)word(p, offset);
}
static int valid_slot(uint8_t x) {
    return x == 0u || x == 2u || x == 4u || x == 5u;
}

uint32_t g2_codec_i2s_configure(void *handle, const void *config) {
    uint32_t *const h = (uint32_t *)handle;
    const uint8_t *const c = (const uint8_t *)config;
    /* Native reads handle+4 before validating the handle. */
    uint32_t const instance = h[1];
    if (handle == 0 || config == 0 || instance >= 2u)
        return 6u;
    if ((h[0] & 0x01ffffffu) != 0x01125125u)
        return 2u;
    if ((h[0] & 0x02000000u) != 0u)
        return 7u;

    const uint8_t *const slots = (const uint8_t *)pointer(c, 0x1cu);
    const uint8_t *const frame = (const uint8_t *)pointer(c, 0x20u);
    uint32_t const n0 = word(slots, 4u), n1 = word(slots, 8u);
    if (n0 >= 9u || n1 >= 9u || n0 == 0u || n0 + n1 >= 9u ||
        !valid_slot(slots[0x14]) || !valid_slot(slots[0x15]) ||
        !valid_slot(slots[0x0c]) || !valid_slot(slots[0x0d]))
        return 6u;

    volatile uint32_t *const mmio = (volatile uint32_t *)(uintptr_t)
        (0x40208000u + (instance << 12));
    mmio[0x48u / 4u] = 0x22u;
    stock_delay_us(200u);
    uint32_t const stereo = c[1] == 1u || c[1] == 2u;
    uint32_t const width0 = slot_width[slots[0x0c]];
    uint32_t const total = width0 * n0 +
        (slots[0] == 0u ? 0u : slot_width[slots[0x0d]] * n1);
    uint32_t frame_width;
    switch (frame[0]) {
    case 0u: frame_width = width0; break;
    case 1u: frame_width = 1u; break;
    case 2u: frame_width = total >> 1; break;
    case 3u:
        frame_width = word(frame, 4u);
        if (frame_width == 0u || total <= frame_width)
            return 6u;
        break;
    default: return 6u;
    }
    mmio[0x44u / 4u] = ((frame_width - 1u) << 20 & 0x0ff00000u) |
        stereo | ((total - 1u) << 4 & 0x0000fff0u) |
        ((frame[8] & 1u) << 16) | ((frame[10] & 1u) << 17) |
        ((c[0] & 1u) << 18) | ((frame[9] & 1u) << 19);
    mmio[0x40u / 4u] = (slots[0x14] & 7u) |
        ((slots[0x16] & 1u) << 3) | ((slots[0x0c] & 7u) << 5) |
        (((n0 - 1u) << 8) & 0x7f00u) | ((slots[0x15] & 7u) << 16) |
        ((word(slots, 0x10u) & 3u) << 19) |
        ((slots[0x0d] & 7u) << 21) |
        (((n1 - 1u) << 24) & 0x7f000000u) |
        ((uint32_t)slots[0] << 31);
    if (c[0] == 1u && word(c, 0x18u) != 0u)
        return 6u;
    uint32_t const source_enabled = c[0] == 1u ||
        (c[0] == 0u && word(c, 0x18u) != 0u);
    mmio[0x54u / 4u] = (mmio[0x54u / 4u] & ~2u) |
        ((c[0] == 0u && word(c, 0x18u) != 0u) ? 0u : 2u);
    mmio[0x54u / 4u] |= 4u;
    ((uint8_t *)handle)[0x60] = (uint8_t)source_enabled;
    if (!source_enabled) {
        h[0x5cu / 4u] = 0x217u;
    } else {
        uint32_t const source = word(c, 4u);
        if ((*chip_revision & 0xffu) == 0x21u &&
            source != 0x100u && source != 0u)
            return 6u;
        if (audio_i2s_clock_source(source) == 7u)
            return 6u;
        h[0x5cu / 4u] = source;
        if (((source & 0x00ffffffu) >> 16) == 1u) {
            double const frequency = number(c, 0x10u);
            uint32_t integral = frequency > 0.0 ? (uint32_t)frequency : 0u;
            uint64_t fraction = (uint64_t)
                ((frequency - (double)integral) * 4294967296.0 + 0.5);
            if (fraction == 0x100000000ull) {
                ++integral;
                fraction = 0u;
            }
            if (integral < 4u)
                return 6u;
            mmio[0x60u / 4u] = integral;
            mmio[0x64u / 4u] = (uint32_t)fraction;
        }
        mmio[0x100u / 4u] = (mmio[0x100u / 4u] & ~0x00100000u) |
            (word(c, 8u) != 0u ? 0x00100000u : 0u);
    }
    mmio[0x10u / 4u] = 32u;
    mmio[0x30u / 4u] = 32u;
    return 0u;
}
