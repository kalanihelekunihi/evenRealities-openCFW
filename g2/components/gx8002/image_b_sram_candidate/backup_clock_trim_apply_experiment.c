/* Stock image-B 0x100039f4..0x10003aff clock-state replay with finite
 * timer wait. The register write order and 64-bit elapsed comparison follow
 * native instructions. The exceptional input-address-zero read remains a
 * named CK804 load rather than a fabricated result.
 */
#include <stdint.h>

extern uint64_t gx8002_image_b_time_10005070(void);

int32_t gx8002_image_b_clock_trim_apply_100039f4(void *state, uint32_t timeout_ms)
{
    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)0xa0005000u;
    volatile uint8_t *const src8 = (volatile uint8_t *)state;
    volatile uint32_t *const src = (volatile uint32_t *)state;

    if (state != 0) {
        reg[0x3cu / 4u] &= ~2u;
        reg[0x3cu / 4u] &= ~1u;
        if (src[0] == 0u)
            return 0;
        uint32_t current;
        uint32_t value;
        reg[0x1cu / 4u] &= ~63u;
        current = reg[0x1cu / 4u]; value = src[0x10u / 4u];
        reg[0x1cu / 4u] = current | value;
        reg[0x20u / 4u] &= ~255u;
        reg[0x24u / 4u] &= ~31u;
        current = reg[0x20u / 4u]; value = src8[0x14u];
        reg[0x20u / 4u] = current | value;
        reg[0x24u / 4u] |= (src[0x14u / 4u] >> 8u) & 31u;
        reg[0x28u / 4u] &= ~7u;
        current = reg[0x28u / 4u]; value = src[0x24u / 4u];
        reg[0x28u / 4u] = current | value;
        reg[0x2cu / 4u] &= ~127u;
        current = reg[0x2cu / 4u]; value = src[0x18u / 4u];
        reg[0x2cu / 4u] = current | value;
        reg[0x30u / 4u] &= ~7u;
        reg[0x30u / 4u] |= src[0x2cu / 4u] & 7u;
        reg[0x30u / 4u] &= ~(16u | 32u);
        current = reg[0x30u / 4u]; value = src[0x20u / 4u] << 4u;
        reg[0x30u / 4u] = current | value;
        reg[0x3cu / 4u] &= ~4u;
        reg[0x3cu / 4u] |= (src[0x1cu / 4u] << 2u) & 4u;
        reg[0x3cu / 4u] |= 2u;
        reg[0x3cu / 4u] |= 1u;
    }

    uint32_t state_word;
    __asm__ volatile ("ld.w %0, (%1, 0)" : "=r"(state_word) : "r"(state) : "memory");
    if (state_word != 1u)
        return 0;

    const uint64_t start = gx8002_image_b_time_10005070();
    const uint32_t limit = timeout_ms * 1000u;
    volatile uint32_t *const ready = (volatile uint32_t *)(uintptr_t)0xa0005098u;
    for (;;) {
        if ((*ready & 8u) != 0u)
            return 0;
        if (gx8002_image_b_time_10005070() - start > (uint64_t)limit)
            return -1;
    }
}
