/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10025e48. Native entry consumes ambient r0 and r4 on
 * branches where a status bit is disabled. The small assembly bridge passes
 * both values to this C core; it does not synthesize initial flags.
 */
#include <stdint.h>

extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);

void gx8002_resident_audio_irq_core_25e48(
    uint32_t ambient_r0, uint32_t ambient_r4)
{
    volatile uint32_t *const audio =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
    volatile uint32_t *const callbacks =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027330);
    volatile uint32_t *const enabled = &audio[0x100u / 4u];
    volatile uint32_t *const status = &audio[0x104u / 4u];

    /* The native prologue probes status bit 24 up to three times. */
    if ((*status & UINT32_C(1 << 24)) == 0u) {
        if ((*status & UINT32_C(1 << 24)) == 0u) (void)*status;
    }

    uint32_t high = ambient_r0;
    if ((*enabled & UINT32_C(1 << 18)) != 0u &&
        (*status & UINT32_C(1 << 18)) != 0u) {
        *status = UINT32_C(1 << 18);
        high = 1u;
    }
    if ((*enabled & UINT32_C(1 << 19)) != 0u &&
        (*status & UINT32_C(1 << 19)) != 0u) {
        high |= 2u;
        *status = UINT32_C(1 << 19);
    }
    if ((*enabled & UINT32_C(1 << 20)) != 0u &&
        (*status & UINT32_C(1 << 20)) != 0u) {
        high |= 4u;
        *status = UINT32_C(1 << 20);
    }
    if (high != 0u) {
        uintptr_t callback = callbacks[0x14u / 4u];
        if (callback != 0u) ((void (*)(uint32_t))callback)(high);
    }

    uint32_t event[3];
    gx8002_xip_memset_102099cc(event, 0u, 12u);
    uint32_t first = ambient_r4;
    if ((*enabled & 1u) != 0u) first = *status & 1u;
    event[0] = audio[0x124u / 4u];
    if ((*enabled & 2u) != 0u && (*status & 2u) != 0u) first |= 2u;
    event[1] = audio[0x148u / 4u];
    if ((*enabled & 4u) != 0u && (*status & 4u) != 0u) first |= 4u;
    event[2] = audio[0x168u / 4u];
    if (first != 0u) {
        uintptr_t callback = callbacks[0x0cu / 4u];
        if (callback != 0u)
            ((void (*)(uint32_t, const uint32_t *))callback)(first, event);
        if ((first & 1u) != 0u) *status = 1u;
        if ((first & 2u) != 0u) *status = 2u;
        if ((first & 4u) != 0u) *status = 4u;
    }

    gx8002_xip_memset_102099cc(event, 0u, 12u);
    uint32_t second = 0u;
    if ((*enabled & 8u) != 0u && (*status & 8u) != 0u) {
        event[0] = audio[0x128u / 4u];
        second = 1u;
    }
    if ((*enabled & 16u) != 0u && (*status & 16u) != 0u) {
        second |= 2u;
        event[1] = audio[0x14cu / 4u];
    }
    if ((*enabled & 32u) != 0u && (*status & 32u) != 0u) {
        second |= 4u;
        event[2] = audio[0x16cu / 4u];
    }
    if (second != 0u) {
        uintptr_t callback = callbacks[0x10u / 4u];
        if (callback != 0u)
            ((void (*)(uint32_t, const uint32_t *))callback)(second, event);
        if ((second & 1u) != 0u) *status = 8u;
        if ((second & 2u) != 0u) *status = 16u;
        if ((second & 4u) != 0u) *status = 32u;
    }

    uint32_t tail = 0u;
    if ((*enabled & UINT32_C(1 << 16)) != 0u &&
        (*status & UINT32_C(1 << 16)) != 0u) {
        *status = UINT32_C(1 << 16);
        tail = 1u;
    }
    if ((*enabled & UINT32_C(1 << 17)) != 0u &&
        (*status & UINT32_C(1 << 17)) != 0u) {
        tail |= 2u;
        *status = UINT32_C(1 << 17);
    }
    uintptr_t callback = callbacks[0x18u / 4u];
    if (callback != 0u) ((void (*)(uint32_t))callback)(tail);
}
