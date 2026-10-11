/* SPDX-License-Identifier: MIT
 * Direct-native image-A XIP 0x10204c64 I2S and 0x10204c90 DAC
 * configuration wrappers. Child register programming 0x10204ab0,
 * 0x102049e8, and 0x10204b5c remains genuine typed source contracts.
 */
#include <stdint.h>

extern void gx8002_xip_aout_i2s_config_10204ab0(
    volatile uint8_t *, const volatile uint8_t *);
extern void gx8002_xip_aout_dac_config_102049e8(
    volatile uint8_t *, const volatile uint8_t *);
extern void gx8002_xip_aout_set_lodac_10204b5c(void);

static uint32_t get32(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}
static void put32(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}
static uint16_t get16(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint16_t *)(const void *)(base + offset);
}
static void put16(volatile uint8_t *base, uint32_t offset, uint16_t value)
{
    *(volatile uint16_t *)(void *)(base + offset) = value;
}

int32_t gx8002_xip_aout_config_i2s_10204c64(
    volatile uint8_t *context, const volatile uint8_t *input)
{
    if (!input) return -1;
    volatile uint8_t *settings =
        (volatile uint8_t *)(uintptr_t)get32(context, 0x30u);
    put32(settings, 0x14u, get32(input, 4u));
    put32(settings, 0x18u, get32(input, 8u));
    put32(settings, 0x20u, get32(input, 0u));
    gx8002_xip_aout_i2s_config_10204ab0(
        (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b00000), settings + 8u);
    gx8002_xip_aout_set_lodac_10204b5c();
    return 0;
}

int32_t gx8002_xip_aout_config_dac_10204c90(
    volatile uint8_t *context, const volatile uint8_t *input)
{
    if (!input) return -1;
    volatile uint8_t *settings =
        (volatile uint8_t *)(uintptr_t)get32(context, 0x30u);
    put32(settings, 0x30u, get32(input, 0u));
    put16(settings, 0x34u, get16(input, 4u));
    put16(settings, 0x36u, get16(input, 6u));
    put16(settings, 0x38u, get16(input, 8u));
    put32(settings, 0x3cu, get32(input, 0x0cu));
    put16(settings, 0x40u, get16(input, 0x10u));
    put16(settings, 0x42u, get16(input, 0x12u));
    put16(settings, 0x44u, get16(input, 0x14u));
    gx8002_xip_aout_dac_config_102049e8(
        (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b00000),
        settings + 0x30u);
    return 0;
}
