/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102049e8 DAC and 0x10204ab0 I2S register
 * programming. Ordered volatile writes retain each stock MMIO transition.
 * This source joins the separately selected config wrappers at
 * 0x10204c64/0x10204c90; Lodac still has its own genuine source contract.
 */
#include <stdint.h>

static uint32_t r32(const volatile uint8_t *base, uint32_t off)
{
    return *(volatile const uint32_t *)(const void *)(base + off);
}
static uint16_t r16(const volatile uint8_t *base, uint32_t off)
{
    return *(volatile const uint16_t *)(const void *)(base + off);
}
static uint8_t r8(const volatile uint8_t *base, uint32_t off)
{
    return base[off];
}
static void w32(volatile uint8_t *base, uint32_t off, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + off) = value;
}
static void replace(volatile uint8_t *base, uint32_t off,
                    uint32_t clear, uint32_t bits)
{
    w32(base, off, (r32(base, off) & ~clear) | bits);
}

void gx8002_xip_aout_i2s_config_10204ab0(
    volatile uint8_t *aout, const volatile uint8_t *settings)
{
    replace(aout, 4u, 0x10000u, (r32(settings, 0x18u) & 1u) << 16u);
    replace(aout, 4u, 0x8000u, 0u);
    replace(aout, 4u, 0x4000u, (r32(settings, 0x20u) & 1u) << 14u);
    replace(aout, 4u, 0x200u, (r32(settings, 4u) & 1u) << 9u);
    replace(aout, 4u, 0x70u, (r32(settings, 8u) & 7u) << 4u);
    replace(aout, 4u, 0x0cu, (r32(settings, 0x0cu) & 3u) << 2u);
    replace(aout, 4u, 0x03u, r32(settings, 0x10u) & 3u);
    replace(aout, 0x10u, 0xc0000000u,
            (r32(settings, 0x24u) & 1u) << 31u);
    w32(aout, 0x10u, (r32(aout, 0x10u) & 0xff000000u) | 0x400u);
}

void gx8002_xip_aout_dac_config_102049e8(
    volatile uint8_t *aout, const volatile uint8_t *settings)
{
    replace(aout, 0x18u, 0xc0000000u, r32(settings, 0u) << 31u);
    replace(aout, 0x18u, 0x00ff0000u, (uint32_t)r8(settings, 4u) << 16u);
    w32(aout, 0x18u, (r32(aout, 0x18u) & 0xffff0000u) |
                       (uint32_t)r16(settings, 6u));
    replace(aout, 0x18u, 0x03000000u,
            ((uint32_t)r16(settings, 8u) & 3u) << 24u);

    replace(aout, 0x1cu, 0xc0000000u, r32(settings, 0x0cu) << 31u);
    replace(aout, 0x1cu, 0x00ff0000u,
            (uint32_t)r8(settings, 0x10u) << 16u);
    w32(aout, 0x1cu, (r32(aout, 0x1cu) & 0xffff0000u) |
                       (uint32_t)r16(settings, 0x12u));
    replace(aout, 0x1cu, 0x03000000u,
            ((uint32_t)r16(settings, 0x14u) & 3u) << 24u);

    replace(aout, 0x2cu, 0xc0000000u, r32(settings, 0x18u) << 31u);
    replace(aout, 0x2cu, 0x03800000u,
            (r32(settings, 0x1cu) & 7u) << 23u);
    replace(aout, 0x2cu, 0x00070000u,
            (r32(settings, 0x20u) & 7u) << 16u);
}
