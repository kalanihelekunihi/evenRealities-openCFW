/* Stock image-B 0x10003b08..0x10003bdd, Grus clock-state register replay.
 * The final source-word read occurs even for an address-zero input in the
 * native body, so that read uses the actual CK804 load instruction. No
 * invented null default or hardware result is supplied here.
 */
#include <stdint.h>

void gx8002_image_b_clock_state_refresh_10003b08(void *state)
{
    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)0xa0005000u;
    volatile uint8_t *const src8 = (volatile uint8_t *)state;
    volatile uint32_t *const src = (volatile uint32_t *)state;

    if (state != 0) {
        reg[0x3cu / 4u] &= ~2u;
        reg[0x3cu / 4u] &= ~1u;
        if (src[0] == 0u)
            return;
        {
            reg[0x1cu / 4u] &= ~63u;
            uint32_t current = reg[0x1cu / 4u];
            uint32_t value = src[0x10u / 4u];
            reg[0x1cu / 4u] = current | value;
            reg[0x20u / 4u] &= ~255u;
            reg[0x24u / 4u] &= ~31u;
            current = reg[0x20u / 4u];
            value = src8[0x14u];
            reg[0x20u / 4u] = current | value;
            reg[0x24u / 4u] |= (src[0x14u / 4u] >> 8u) & 31u;
            reg[0x28u / 4u] &= ~7u;
            current = reg[0x28u / 4u];
            value = src[0x24u / 4u];
            reg[0x28u / 4u] = current | value;
            reg[0x2cu / 4u] &= ~127u;
            current = reg[0x2cu / 4u];
            value = src[0x18u / 4u];
            reg[0x2cu / 4u] = current | value;
            reg[0x30u / 4u] &= ~7u;
            reg[0x30u / 4u] |= src[0x2cu / 4u] & 7u;
            reg[0x30u / 4u] &= ~(16u | 32u);
            current = reg[0x30u / 4u];
            value = src[0x20u / 4u] << 4u;
            reg[0x30u / 4u] = current | value;
            reg[0x3cu / 4u] &= ~4u;
            reg[0x3cu / 4u] |= (src[0x1cu / 4u] << 2u) & 4u;
            reg[0x3cu / 4u] |= 2u;
            reg[0x3cu / 4u] |= 1u;
        }
    }

    uint32_t state_word;
    __asm__ volatile ("ld.w %0, (%1, 0)" : "=r"(state_word) : "r"(state) : "memory");
    if (state_word == 1u) {
        while ((reg[0x98u / 4u] & 8u) == 0u) { }
    }
}
