/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x10206e9c, 0x10206ec8, 0x10206f08, 0x10207394.
 * Runtime context pointers are authenticated XIP literal words.
 */
#include <stdint.h>

const uint32_t *gx8002_xip_tws_clock_10206e9c(void)
{
    return (const uint32_t *)(uintptr_t)UINT32_C(0x20027b60);
}

uint32_t gx8002_xip_tws_context_10206ec8(
    uint32_t index, void **out_context, void *out_auxiliary)
{
    uint32_t offset = (index % 3u) * UINT32_C(0x2140);
    uint8_t *const base = (uint8_t *)(uintptr_t)UINT32_C(0x20027b60);
    uint8_t *const context = base + 0x80u + offset;
    *(uint32_t *)(void *)context = UINT32_C(0x20027b60);
    *(uint32_t *)(void *)(context + 0x10u) =
        (uint32_t)(uintptr_t)(context + 0x20u);
    *out_context = context;
    *(uint32_t *)out_auxiliary = UINT32_C(0x2140);
    return 0u;
}

uint32_t gx8002_xip_tws_item_10206f08(
    void *context, uint32_t index, uint32_t channel)
{
    const uint8_t *const record = (const uint8_t *)context;
    const uint8_t *const header = *(const uint8_t *const *)(const void *)record;
    uint32_t sequence = *(const uint32_t *)(const void *)(record + 8u);
    uint32_t frames = *(const uint32_t *)(const void *)(header + 0x3cu);
    uint32_t frame = sequence % frames;
    uint32_t stride = *(const uint32_t *)(const void *)(header + 0x28u);
    uint32_t channels = *(const uint32_t *)(const void *)(header + 0x24u);
    uint32_t rate = *(const uint32_t *)(const void *)(header + 0x20u) *
                    *(const uint32_t *)(const void *)(header + 0x1cu);
    uint32_t base = *(const uint32_t *)(const void *)(header + 0x50u);
    return base + (channel + index * stride + frame * channels) *
                  (rate / 1000u) * 2u;
}

uint32_t gx8002_xip_tws_mode_10207394(void)
{
    volatile uint32_t *const audio_input =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002ecb0);
    return audio_input[3];
}
