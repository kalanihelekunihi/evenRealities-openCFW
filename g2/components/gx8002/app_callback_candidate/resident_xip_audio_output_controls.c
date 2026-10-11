/* SPDX-License-Identifier: MIT
 * Native image-A XIP AOUT controls 0x10204cdc..0x10204d35,
 * 0x10204e6c..0x10204ebd, and 0x1020508c..0x102050c9.
 * Direct movih establishes two distinct hardware blocks: 0xa0b00000
 * playback control and 0xa0b80000 sample-buffer/SDC registers.
 */
#include <stdint.h>

extern void g2_codec_header_sync(void *, uint32_t);
extern void gx8002_resident_delay_ms_2598c(uint32_t);
extern void gx8002_xip_aout_play_check_idle_102049d8(
    volatile uint8_t *, uint32_t);
extern void gx8002_xip_aout_frame_over_enable_102049c8(
    volatile uint8_t *, uint32_t);

static volatile uint8_t *const playback =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b00000);
static volatile uint8_t *const sample =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b80000);

static uint32_t read32(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}
static void write32(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

uint32_t gx8002_xip_aout_set_fixed_src_10204cdc(
    uint32_t unused, uint32_t source)
{
    (void)unused;
    write32(playback, 0x10u, read32(playback, 0x10u) | UINT32_C(0x80000000));
    uint32_t value = read32(playback, 0x10u) & UINT32_C(0xff000000);
    write32(playback, 0x10u, value | ((source << 8u) & UINT32_C(0x00ffffff)));
    return 0u;
}

uint32_t gx8002_xip_aout_get_sdc_addr_10204cfc(void)
{
    return read32(sample, 0x10u);
}

uint32_t gx8002_xip_aout_drain_frame_10204d04(volatile uint8_t *context)
{
    context[0x1cu] = 0u;
    context[0x1au] = 1u;
    gx8002_xip_aout_play_check_idle_102049d8(playback, 1u);
    gx8002_xip_aout_frame_over_enable_102049c8(playback, 1u);
    while (context[0x1cu] == 0u)
        gx8002_resident_delay_ms_2598c(1u);
    return 0u;
}

int32_t gx8002_xip_aout_config_buffer_10204e6c(
    uint32_t ignored, const uint32_t *configuration)
{
    (void)ignored;
    uint32_t primary = configuration[0];
    if (primary == 0u || (primary & 0xfu) != 0u) return -1;
    write32(sample, 4u, primary + UINT32_C(0xe0000000));
    g2_codec_header_sync((void *)(uintptr_t)primary, configuration[2]);
    uint32_t secondary = configuration[1];
    if (secondary != 0u) {
        if ((secondary & 0xfu) != 0u) return -1;
        write32(sample, 8u, secondary + UINT32_C(0xe0000000));
        g2_codec_header_sync((void *)(uintptr_t)secondary, configuration[2]);
    }
    write32(sample, 0x0cu, configuration[2]);
    return 0;
}

uint32_t gx8002_xip_aout_set_mute_1020508c(
    volatile uint8_t *context, uint32_t enabled)
{
    uint32_t flag = enabled != 0u;
    write32(playback, 4u,
        (read32(playback, 4u) & ~UINT32_C(0x200)) | (flag << 9u));
    write32(playback, 0x14u,
        (read32(playback, 0x14u) & ~UINT32_C(0x800)) | (flag << 11u));
    write32(playback, 0x14u,
        (read32(playback, 0x14u) & ~UINT32_C(0x8000)) | (flag << 15u));
    *(volatile uint16_t *)(void *)(context + 0x10u) = 1u;
    return 0u;
}
