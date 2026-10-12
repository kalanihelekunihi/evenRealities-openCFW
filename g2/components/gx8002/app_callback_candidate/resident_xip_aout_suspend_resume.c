/* SPDX-License-Identifier: MIT
 * Image-A XIP AOUT 0x102049b0, 0x10204ec0, and 0x1020521c.
 * The register base is 0xa0b00000 in direct C-SKY movih operands.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_xip_aout_play_check_idle_102049d8(
    volatile uint8_t *, uint32_t);
extern void gx8002_xip_aout_frame_over_enable_102049c8(
    volatile uint8_t *, uint32_t);

static volatile uint8_t *const aout =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b00000);

static uint32_t read32(uint32_t offset)
{
    return *(volatile uint32_t *)(void *)(aout + offset);
}
static void write32(uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(aout + offset) = value;
}

uint32_t gx8002_xip_audio_channel_field_102049b0(
    uint32_t register_index, uint32_t channel)
{
    /* Native 0x102049b0 adds ten to numeric r0, then uses
     * 0xa0a00000 + ((r0 + 10) << 2); r0 is not a pointer. */
    volatile uint32_t *field =
        (volatile uint32_t *)(uintptr_t)
            (UINT32_C(0xa0a00000) + ((register_index + 10u) << 2u));
    *field = (*field & UINT32_C(0xffff03ff)) |
             ((channel & UINT32_C(0x3f)) << 10u);
    return 0u;
}

uint32_t gx8002_xip_aout_suspend_10204ec0(volatile uint8_t *context)
{
    if (context[0x1bu] != 0u) {
        write32(8u, read32(8u) & ~UINT32_C(1));
        write32(0x0cu, read32(0x0cu) & UINT32_C(1));
    }
    if (context[0x1au] != 0u) {
        gx8002_xip_aout_play_check_idle_102049d8(aout, 0u);
        gx8002_xip_aout_frame_over_enable_102049c8(aout, 0u);
        write32(0x0cu, read32(0x0cu) & UINT32_C(2));
    }
    gx8002_resident_platform_gate_25080(11u, 0u);
    gx8002_resident_platform_gate_25080(15u, 0u);
    return 0u;
}

uint32_t gx8002_xip_aout_resume_1020521c(volatile uint8_t *context)
{
    gx8002_resident_platform_gate_25080(11u, 1u);
    gx8002_resident_platform_gate_25080(15u, 1u);
    if (context[0x1bu] != 0u) write32(8u, read32(8u) | UINT32_C(1));
    if (context[0x1au] != 0u) context[0x1au] = 0u;
    return 0u;
}
