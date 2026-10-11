/* SPDX-License-Identifier: MIT
 * Native XIP 0x10207660 and 0x102047b8. The startup call passes
 * interrupt mask 0x30007 and enable=1 in r0/r1. State literal at
 * 0x1020767c resolves to 0x2002ecb0.
 */
#include <stdint.h>

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);

uint32_t gx8002_xip_audio_set_interrupt_enable_102047b8(
    uint32_t mask, uint32_t enabled)
{
    if (enabled != 0u) {
        ain[0x104u / 4u] = mask;
        ain[0x100u / 4u] = ain[0x100u / 4u] | mask;
    } else {
        ain[0x100u / 4u] = ain[0x100u / 4u] & ~mask;
        ain[0x104u / 4u] = mask;
    }
    return 0u;
}

void gx8002_xip_audio_standby_startup_10207660(void)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002ecb0);
    state[0x10u] = (state[0x10u] & 0x0fu) | 0x10u;
    (void)gx8002_xip_audio_set_interrupt_enable_102047b8(0x30007u, 1u);
}
