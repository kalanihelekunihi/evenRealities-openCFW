/* SPDX-License-Identifier: MIT
 * Native audio output table config target 0x1000687c..0x1000694b.
 * Ordered MMIO writes preserve the stock register transaction sequence.
 */
#include <stdint.h>

#define LATE_AUDIO __attribute__((section(".image_b_late_audio")))

extern void gx8002_image_b_audio_mode_10005ec8(void);

LATE_AUDIO
int32_t gx8002_image_b_audio_out_config_hardware_1000687c(
    volatile uint8_t *state, const uint32_t *configuration)
{
    if (configuration == (const uint32_t *)0) return -1;
    volatile uint32_t *audio = (volatile uint32_t *)(uintptr_t)
        *(volatile uint32_t *)(volatile void *)(state + 0x30u);
    uint32_t first = configuration[0];
    uint32_t second = configuration[1];
    uint32_t third = configuration[2];
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;

    audio[0x20u / 4u] = first;
    uint32_t control = dac[1];
    audio[0x14u / 4u] = second;
    audio[0x18u / 4u] = third;
    dac[1] = (control & ~(1u << 16)) | ((first << 16) & (1u << 16));
    control = dac[1];
    dac[1] = (control & ~(1u << 15)) |
             ((audio[0x24u / 4u] << 15) & (1u << 15));
    control = dac[1];
    dac[1] = (control & ~(1u << 14)) |
             ((audio[0x28u / 4u] << 14) & (1u << 14));
    control = dac[1];
    dac[1] = (control & ~(1u << 9)) |
             ((audio[0x0cu / 4u] << 9) & (1u << 9));
    control = dac[1];
    dac[1] = (control & ~(7u << 4)) |
             ((audio[0x10u / 4u] << 4) & (7u << 4));
    control = dac[1];
    dac[1] = (control & ~(3u << 2)) | ((second << 2) & (3u << 2));
    control = dac[1];
    dac[1] = (control & ~3u) | (third & 3u);
    control = dac[4];
    dac[4] = (control & ~(1u << 31)) |
             ((audio[0x2cu / 4u] << 31) & (1u << 31));
    control = dac[4];
    dac[4] = (control & UINT32_C(0xff000000)) | (1u << 10);
    gx8002_image_b_audio_mode_10005ec8();
    return 0;
}

LATE_AUDIO
int32_t gx8002_image_b_audio_out_config_dac_1000694c(
    volatile uint8_t *state, const uint8_t *configuration)
{
    if (configuration == (const uint8_t *)0) return -1;
    volatile uint8_t *audio = (volatile uint8_t *)(uintptr_t)
        *(volatile uint32_t *)(volatile void *)(state + 0x30u);
    uint32_t flag = *(const uint32_t *)(const void *)(configuration + 0u);
    uint16_t a = *(const uint16_t *)(const void *)(configuration + 4u);
    uint16_t b = *(const uint16_t *)(const void *)(configuration + 6u);
    uint16_t c = *(const uint16_t *)(const void *)(configuration + 8u);
    uint32_t second_flag = *(const uint32_t *)(const void *)(configuration + 12u);
    uint16_t d = *(const uint16_t *)(const void *)(configuration + 16u);
    uint16_t e = *(const uint16_t *)(const void *)(configuration + 18u);
    uint16_t f = *(const uint16_t *)(const void *)(configuration + 20u);
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;

    *(volatile uint32_t *)(volatile void *)(audio + 0x30u) = flag;
    *(volatile uint16_t *)(volatile void *)(audio + 0x34u) = a;
    *(volatile uint16_t *)(volatile void *)(audio + 0x36u) = b;
    *(volatile uint16_t *)(volatile void *)(audio + 0x38u) = c;
    *(volatile uint32_t *)(volatile void *)(audio + 0x3cu) = second_flag;
    *(volatile uint16_t *)(volatile void *)(audio + 0x40u) = d;
    *(volatile uint16_t *)(volatile void *)(audio + 0x42u) = e;
    *(volatile uint16_t *)(volatile void *)(audio + 0x44u) = f;

    uint32_t control = dac[6];
    dac[6] = (control & ~(1u << 31)) | (flag << 31);
    control = dac[6];
    dac[6] = (control & UINT32_C(0xff00ffff)) | ((a & 0xffu) << 16);
    control = dac[6];
    dac[6] = (control & UINT32_C(0xffff0000)) | b;
    control = dac[6];
    dac[6] = (control & ~(3u << 24)) | ((c & 3u) << 24);
    control = dac[7];
    dac[7] = (control & ~(1u << 31)) | (second_flag << 31);
    control = dac[7];
    dac[7] = (control & UINT32_C(0xff00ffff)) | ((d & 0xffu) << 16);
    control = dac[7];
    dac[7] = (control & UINT32_C(0xffff0000)) | e;
    control = dac[7];
    dac[7] = (control & ~(3u << 24)) | ((f & 3u) << 24);
    control = dac[11];
    uint32_t extension = *(volatile uint32_t *)(volatile void *)(audio + 0x48u);
    dac[11] = (control & ~(1u << 31)) | (extension << 31);
    control = dac[11];
    extension = *(volatile uint32_t *)(volatile void *)(audio + 0x4cu);
    dac[11] = (control & UINT32_C(0xfc7fffff)) |
              ((extension << 23) & UINT32_C(0x03800000));
    control = dac[11];
    extension = *(volatile uint32_t *)(volatile void *)(audio + 0x50u);
    dac[11] = (control & UINT32_C(0xfff8ffff)) |
              ((extension << 16) & UINT32_C(0x00070000));
    return 0;
}
