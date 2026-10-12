/* SPDX-License-Identifier: MIT
 * Native table target 0x100067ec and registered IRQ child 0x1000669c.
 * The unusual zero-address write on unsupported init states follows the
 * stock CFG; no invented recovery/default handle is supplied.
 */
#include <stdint.h>

#define LATE_AUDIO __attribute__((section(".image_b_late_audio")))

extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t line, int32_t (*handler)(int32_t, void *), uint32_t argument);
extern uint32_t gx8002_image_b_audio_out_state_address_10006a80(void);

LATE_AUDIO
int32_t gx8002_image_b_audio_out_irq_1000669c(int32_t line, void *argument)
{
    if (line != 13) return 0;
    volatile uint8_t *state = (volatile uint8_t *)argument;
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    uint32_t pending = dac[3] & dac[2];
    if ((pending & 4u) != 0u) {
        dac[6] &= UINT32_C(0x7fffffff);
        dac[3] &= 4u;
        dac[2] &= ~4u;
    }
    if ((pending & 8u) != 0u) {
        dac[7] &= UINT32_C(0x7fffffff);
        dac[3] &= 8u;
        dac[2] &= ~8u;
    }
    if ((pending & 64u) != 0u) dac[3] &= 64u;
    if ((pending & 1u) != 0u) {
        dac[3] &= 1u;
        uint32_t callback =
            *(volatile uint32_t *)(volatile void *)(state + 0x28u);
        if (callback != 0u) {
            uint32_t first =
                *(volatile uint32_t *)(volatile void *)(state + 0x20u);
            uint32_t second =
                *(volatile uint32_t *)(volatile void *)(state + 0x24u);
            ((void (*)(uint32_t, uint32_t))(uintptr_t)callback)(first, second);
        }
    }
    if ((pending & 2u) != 0u) {
        dac[3] &= 4u;
        dac[3] &= 8u;
        dac[3] &= 64u;
        dac[3] &= 1u;
        dac[0] &= ~2u;
        dac[2] &= ~2u;
        dac[3] &= 2u;
        state[0x1cu] = 1u;
        uint32_t callback =
            *(volatile uint32_t *)(volatile void *)(state + 0x2cu);
        if (callback != 0u) ((void (*)(void))(uintptr_t)callback)();
    }
    return 0;
}

LATE_AUDIO
uint32_t gx8002_image_b_audio_out_alloc_native_100067ec(uint32_t mode)
{
    volatile uint8_t *const root = (volatile uint8_t *)(uintptr_t)0x20016c84u;
    uintptr_t chosen = root[4u];
    if (chosen != 0u) {
        chosen = 0u;
    } else if (*(volatile uint32_t *)(volatile void *)(root + 8u) == 0u) {
        if (root[0x0cu] == (uint8_t)mode) {
            gx8002_image_b_zero_100113c4((void *)(root + 0x10u), 0u, 36u);
            root[4u] = 1u;
            chosen = (uintptr_t)root;
        }
    }
    volatile uint8_t *state = (volatile uint8_t *)chosen;
    *(volatile uint32_t *)(volatile void *)(state + 0x14u) = 0u;
    state[0x18u] = (uint8_t)mode;
    uint32_t audio_state = gx8002_image_b_audio_out_state_address_10006a80();
    *(volatile uint32_t *)(volatile void *)(state + 0x30u) = audio_state;
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    dac[3] |= 1u << 21;
    dac[0] &= UINT32_C(0x7fffffff);
    volatile uint32_t *const audio = (volatile uint32_t *)(uintptr_t)audio_state;
    dac[0] = (dac[0] & ~2u) | ((audio[0] << 1) & 2u);
    dac[0] = (dac[0] & ~1u) | (audio[1] & 1u);
    dac[1] &= ~(1u << 8);
    gx8002_image_b_request_irq_10004844(
        13u, gx8002_image_b_audio_out_irq_1000669c, (uint32_t)chosen);
    return (uint32_t)chosen;
}
