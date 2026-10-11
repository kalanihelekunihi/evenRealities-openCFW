/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10204d38..0x10204e67 PCM configuration.
 * Direct listing establishes unsigned rate division, the eight accepted
 * ratios, A0B80000 SDC flag register, and call order into source-owned
 * I2S/DAC/Lodac lowers. Exact mismatch format data at XIP 0x1020a9b0.
 * A zero clock divisor has no supported stock behavior/input contract.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void gx8002_xip_aout_i2s_config_10204ab0(
    volatile uint8_t *, const volatile uint8_t *);
extern void gx8002_xip_aout_dac_config_102049e8(
    volatile uint8_t *, const volatile uint8_t *);
extern void gx8002_xip_aout_set_lodac_10204b5c(void);

static const char mismatch_format[] =
    "The current clock and sampling rate do not match. \n"
    " please,Please use audio with sampling rates of 8k, 16k, and 48k!\n";
_Static_assert(sizeof(mismatch_format) == 118u,
               "stock XIP 0x1020a9b0 format extent");

static uint32_t pcm_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}
static void pcm_store(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

int32_t gx8002_xip_aout_config_pcm_10204d38(
    volatile uint8_t *context, const volatile uint8_t *input)
{
    uint8_t bits = input[5u];
    uint32_t bit_mode;
    if (bits == 16u) bit_mode = 8u;
    else if (bits == 32u) bit_mode = 0u;
    else return -1;

    uint32_t sampling = pcm_word(input, 8u);
    if (sampling == 0u) {
        (void)gx8002_xip_tws_publish_10206c24(mismatch_format);
        return -1;
    }
    uint32_t clock = pcm_word(input, 0u);
    uint32_t ratio = sampling / clock;
    if (sampling != ratio * clock) {
        (void)gx8002_xip_tws_publish_10206c24(mismatch_format);
        return -1;
    }
    uint32_t code;
    switch (ratio) {
    case 128u: code = 3u; break;
    case 192u: code = 7u; break;
    case 256u: code = 0u; break;
    case 384u: code = 4u; break;
    case 512u: code = 1u; break;
    case 768u: code = 5u; break;
    case 1024u: code = 2u; break;
    case 1536u: code = 6u; break;
    default: return -1;
    }
    volatile uint8_t *settings =
        (volatile uint8_t *)(uintptr_t)pcm_word(context, 0x30u);
    pcm_store(settings, 0x10u, code);
    context[0x19u] = bits >> 3u;

    volatile uint8_t *const sample =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b80000);
    pcm_store(sample, 0u, (pcm_word(sample, 0u) & ~UINT32_C(0xf)) | bit_mode);
    uint32_t flags = pcm_word(sample, 0u);
    flags = (flags & ~UINT32_C(0x40)) | ((input[4u] != 1u) << 6u);
    pcm_store(sample, 0u, flags);
    flags = pcm_word(sample, 0u);
    flags = (flags & ~UINT32_C(0x80)) | ((input[6u] != 0u) << 7u);
    pcm_store(sample, 0u, flags);
    flags = pcm_word(sample, 0u);
    flags = (flags & ~UINT32_C(0x30)) | ((input[7u] != 0u) << 4u);
    pcm_store(sample, 0u, flags);

    settings = (volatile uint8_t *)(uintptr_t)pcm_word(context, 0x30u);
    volatile uint8_t *const playback =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b00000);
    gx8002_xip_aout_i2s_config_10204ab0(playback, settings + 8u);
    settings = (volatile uint8_t *)(uintptr_t)pcm_word(context, 0x30u);
    gx8002_xip_aout_dac_config_102049e8(playback, settings + 0x30u);
    gx8002_xip_aout_set_lodac_10204b5c();
    return 0;
}
