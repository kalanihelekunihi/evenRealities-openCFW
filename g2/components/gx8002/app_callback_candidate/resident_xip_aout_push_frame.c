/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102051a8 AOUT frame submission.
 * Direct movih distinguishes sample MMIO 0xa0b80000 from playback
 * control MMIO 0xa0b00000. Context byte +0x19 is a nonzero native
 * divisor precondition; no substitute width is invented here.
 */
#include <stdint.h>

extern void gx8002_resident_memcpy_25738(void *, const void *, uint32_t);
extern void gx8002_xip_aout_play_check_idle_102049d8(
    volatile uint8_t *, uint32_t);
extern void gx8002_xip_aout_frame_over_enable_102049c8(
    volatile uint8_t *, uint32_t);

static volatile uint32_t *const sample =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b80000);
static volatile uint8_t *const playback =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b00000);

uint32_t gx8002_xip_aout_push_frame_102051a8(
    volatile uint8_t *context, const void *frame)
{
    if (frame == (void *)0) return UINT32_MAX;
    gx8002_resident_memcpy_25738((void *)(context + 0x20u), frame, 8u);
    uint32_t first = *(volatile uint32_t *)(void *)(context + 0x20u);
    uint32_t last = *(volatile uint32_t *)(void *)(context + 0x24u);
    uint32_t width = context[0x19u];
    uint32_t span = (uint32_t)((int32_t)((last + 1u) - first) /
                               (int32_t)width);
    (void)sample[0x14u / 4u];
    sample[0x14u / 4u] = first;
    (void)sample[0x18u / 4u];
    sample[0x18u / 4u] = last;
    sample[0x24u / 4u] = (sample[0x24u / 4u] & UINT32_C(0xff000000)) |
                         (span & UINT32_C(0x007fffff));
    sample[0x2cu / 4u] = sample[0x2cu / 4u] | 2u;
    if (context[0x1au] == 0u) {
        if (*(volatile uint32_t *)(void *)(context + 0x2cu) == 0u)
            return 0u;
        context[0x1au] = 1u;
        gx8002_xip_aout_play_check_idle_102049d8(playback, 1u);
        gx8002_xip_aout_frame_over_enable_102049c8(playback, 1u);
    }
    return 0u;
}
