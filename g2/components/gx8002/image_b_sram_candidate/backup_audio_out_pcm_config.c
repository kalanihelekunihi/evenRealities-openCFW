/* SPDX-License-Identifier: MIT
 * Native image-B table target 0x100061f4..0x100064e7. The validation,
 * sample-clock ratio map, state byte, MMIO bitfields and final audio-mode
 * call follow the stock instruction CFG. Device timing remains untested.
 */
#include <stdint.h>

#define LATE_AUDIO __attribute__((section(".image_b_late_audio")))

extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern void gx8002_image_b_audio_mode_10005ec8(void);

static uint32_t word_at(const uint8_t *base, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(base + offset);
}

static uint16_t half_at(const uint8_t *base, uint32_t offset)
{
    return *(const uint16_t *)(const void *)(base + offset);
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_pcm_config_100061f4(
    volatile uint8_t *state, const uint8_t *configuration)
{
    uint8_t width = configuration[5];
    if (width != 16u && width != 32u) return -1;
    uint32_t sample_rate = word_at(configuration, 8u);
    if (sample_rate == 0u) goto bad_clock;
    uint32_t clock = word_at(configuration, 0u);
    uint32_t ratio = sample_rate / clock;
    if (sample_rate % clock != 0u) goto bad_clock;

    uint32_t code;
    switch (ratio) {
    case 128u:  code = 3u; break;
    case 192u:  code = 7u; break;
    case 256u:  code = 0u; break;
    case 384u:  code = 4u; break;
    case 512u:  code = 1u; break;
    case 768u:  code = 5u; break;
    case 1024u: code = 2u; break;
    case 1536u: code = 6u; break;
    default: return -1;
    }

    volatile uint8_t *audio_bytes = (volatile uint8_t *)(uintptr_t)
        *(volatile uint32_t *)(volatile void *)(state + 0x30u);
    volatile uint32_t *audio = (volatile uint32_t *)(volatile void *)audio_bytes;
    audio[4] = code;
    state[0x19u] = width >> 3;
    volatile uint32_t *const audio_mmio =
        (volatile uint32_t *)(uintptr_t)0xa0b80000u;
    uint32_t control = audio_mmio[0];
    audio_mmio[0] = (control & ~15u) | (width == 16u ? 8u : 0u);
    control = audio_mmio[0];
    audio_mmio[0] = (control & ~(1u << 6)) |
                    ((uint32_t)(configuration[4] == 1u) << 6);
    control = audio_mmio[0];
    audio_mmio[0] = (control & ~(1u << 7)) |
                    ((uint32_t)(configuration[6] != 0u) << 7);
    control = audio_mmio[0];
    audio_mmio[0] = (control & ~(3u << 4)) |
                    ((uint32_t)(configuration[7] != 0u) << 4);

    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    control = dac[1];
    dac[1] = (control & ~(1u << 16)) | ((audio[8] << 16) & (1u << 16));
    control = dac[1];
    dac[1] = (control & ~(1u << 15)) | ((audio[9] << 15) & (1u << 15));
    control = dac[1];
    dac[1] = (control & ~(1u << 14)) | ((audio[10] << 14) & (1u << 14));
    control = dac[1];
    dac[1] = (control & ~(1u << 9)) | ((audio[3] << 9) & (1u << 9));
    control = dac[1];
    dac[1] = (control & ~(7u << 4)) | (code << 4);
    control = dac[1];
    dac[1] = (control & ~(3u << 2)) | ((audio[5] << 2) & (3u << 2));
    control = dac[1];
    dac[1] = (control & ~3u) | (audio[6] & 3u);
    control = dac[4];
    dac[4] = (control & ~(1u << 31)) | (audio[11] << 31);
    control = dac[4];
    dac[4] = (control & UINT32_C(0xff000000)) | (1u << 10);

    control = dac[6];
    dac[6] = (control & ~(1u << 31)) | (audio[12] << 31);
    control = dac[6];
    dac[6] = (control & UINT32_C(0xff00ffff)) |
             ((uint32_t)audio_bytes[0x34u] << 16);
    control = dac[6];
    dac[6] = (control & UINT32_C(0xffff0000)) |
             half_at((const uint8_t *)(const void *)audio_bytes, 0x36u);
    control = dac[6];
    dac[6] = (control & ~(3u << 24)) |
             ((uint32_t)(half_at((const uint8_t *)(const void *)audio_bytes,
                                  0x38u) & 3u) << 24);
    control = dac[7];
    dac[7] = (control & ~(1u << 31)) | (audio[15] << 31);
    control = dac[7];
    dac[7] = (control & UINT32_C(0xff00ffff)) |
             ((uint32_t)audio_bytes[0x40u] << 16);
    control = dac[7];
    dac[7] = (control & UINT32_C(0xffff0000)) |
             half_at((const uint8_t *)(const void *)audio_bytes, 0x42u);
    control = dac[7];
    dac[7] = (control & ~(3u << 24)) |
             ((uint32_t)(half_at((const uint8_t *)(const void *)audio_bytes,
                                  0x44u) & 3u) << 24);
    control = dac[11];
    dac[11] = (control & ~(1u << 31)) | (audio[18] << 31);
    control = dac[11];
    dac[11] = (control & UINT32_C(0xfc7fffff)) |
              ((audio[19] << 23) & UINT32_C(0x03800000));
    control = dac[11];
    dac[11] = (control & UINT32_C(0xfff8ffff)) |
              ((audio[20] << 16) & UINT32_C(0x00070000));
    gx8002_image_b_audio_mode_10005ec8();
    return 0;

bad_clock:
    (void)gx8002_image_b_heap_log_10009934(
        "The current clock and sampling rate do not match. \n"
        " please,Please use audio with sampling rates of 8k, 16k, and 48k!\n");
    return -1;
}
