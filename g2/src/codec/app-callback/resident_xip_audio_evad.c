/* SPDX-License-Identifier: MIT
 * Native EVAD enable/threshold bodies 0x102043fc/0x102044e0.
 * Callers supply valid channels 1,2,4; native invalid-channel path
 * dereferences null and is not a supported product input.
 */
#include <stdint.h>

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);

static volatile uint32_t *evad(uint32_t channel)
{
    if (channel == 1u) return &ain[0x10u / 4u];
    if (channel == 2u) return &ain[0x30u / 4u];
    return &ain[0x50u / 4u]; /* channel 4 precondition */
}

void gx8002_xip_audio_set_evad_enable_102043fc(
    uint32_t channel, uint32_t enabled, uint32_t wake, uint32_t sign)
{
    volatile uint32_t *selected = evad(channel);
    if (channel == 2u || channel == 4u)
        selected[0] &= ~UINT32_C(0x10000000);
    uint32_t bit = channel == 1u ? 18u : channel == 2u ? 19u : 20u;
    ain[0x100u / 4u] =
        (ain[0x100u / 4u] & ~(UINT32_C(1) << bit)) |
        ((enabled & 1u) << bit);
    selected[0] |= UINT32_C(1) << 26u;
    while (selected[5] != 0u) {}
    selected[0] &= ~(UINT32_C(1) << 26u);
    selected[0] = (selected[0] & ~(UINT32_C(1) << 27u)) |
                  ((enabled == 0u ? 1u : 0u) << 27u);
    selected[0] = (selected[0] & ~(UINT32_C(1) << 25u)) |
                  ((wake == 0u ? 1u : 0u) << 25u);
    selected[0] |= UINT32_C(1) << 24u;
    selected[0] = (selected[0] & UINT32_C(0xffff0000)) | 0x6000u;
    selected[0] = (selected[0] & UINT32_C(0x7fffffff)) | (sign << 31u);
    selected[1] &= UINT32_C(0xff00ffff);
    selected[1] = (selected[1] & UINT32_C(0xffff0000)) | 0x10u;
}

uint32_t gx8002_xip_audio_set_evad_threshold_102044e0(
    uint32_t channel, uint32_t first, uint32_t second, uint32_t third)
{
    volatile uint32_t *selected = evad(channel);
    if (channel == 2u || channel == 4u)
        selected[0] &= ~UINT32_C(0x10000000);
    selected[2] = first;
    selected[3] = second;
    selected[4] = third;
    return 0u;
}
