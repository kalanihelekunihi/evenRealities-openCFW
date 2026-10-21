/* SPDX-License-Identifier: MIT
 * Direct-native image-A XIP 0x102052e0 free, 0x10205318 callback
 * configuration, 0x10205344 exit. AOUT playback and sample MMIO blocks
 * and register read/write order are fixed by native disassembly.
 */
#include <stdint.h>

extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);
extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);

static volatile uint32_t *const playback =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b00000);
static volatile uint32_t *const sample =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b80000);

int32_t gx8002_xip_aout_free_102052e0(volatile uint8_t *context)
{
    playback[0x08u / 4u] = playback[0x08u / 4u] & ~UINT32_C(1);
    (void)sample[0x14u / 4u];
    sample[0x14u / 4u] = 0u;
    (void)sample[0x18u / 4u];
    sample[0x18u / 4u] = 0u;
    (void)gx8002_xip_memset_102099cc((void *)(context + 0x10u), 0, 36u);
    if (context && context[4u]) context[4u] = 0u;
    return 0;
}

uint32_t gx8002_xip_aout_config_cb_10205318(
    volatile uint8_t *context, const uint32_t *callbacks)
{
    if (callbacks[0] != 0u) {
        playback[0x08u / 4u] = playback[0x08u / 4u] | 1u;
        *(volatile uint32_t *)(void *)(context + 0x28u) = callbacks[0];
        context[0x1bu] = 1u;
    }
    if (callbacks[1] != 0u) {
        *(volatile uint32_t *)(void *)(context + 0x2cu) = callbacks[1];
        context[0x1au] = 0u;
    }
    return 0u;
}

uint32_t gx8002_xip_aout_exit_10205344(void)
{
    playback[0x20u / 4u] = playback[0x20u / 4u] & ~UINT32_C(2);
    playback[0x20u / 4u] = playback[0x20u / 4u] & ~UINT32_C(4);
    playback[0x20u / 4u] = playback[0x20u / 4u] & ~UINT32_C(8);
    gx8002_resident_platform_gate_25080(11u, 0u);
    gx8002_resident_platform_gate_25080(15u, 0u);
    return 0u;
}
