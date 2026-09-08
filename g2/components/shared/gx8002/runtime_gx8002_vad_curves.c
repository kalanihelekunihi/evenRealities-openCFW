/* SPDX-License-Identifier: MIT */
/* GX8002 FFT VAD curve controls. Public SDK prototypes use 16-bit inputs.
 * Each accepted pair is committed with two independent read/write cycles;
 * the second cycle must observe any intervening hardware change.
 */
#include <stdint.h>
#if defined(OPEN_CFW_GX8002_VAD_HOST_TEST)
extern uint32_t open_cfw_gx8002_vad_read(unsigned index);
extern void open_cfw_gx8002_vad_write(unsigned index, uint32_t value);
#define READ(index) open_cfw_gx8002_vad_read(index)
#define WRITE(index, value) open_cfw_gx8002_vad_write(index, value)
#else
#define READ(index) (((volatile uint32_t *)0xA0A00000U)[index])
#define WRITE(index, value) ((((volatile uint32_t *)0xA0A00000U)[index]) = (value))
#endif

typedef union {
    uint32_t word;
    struct { uint32_t low : 16, high : 16; } field;
} curve_register;
_Static_assert(sizeof(curve_register) == 4, "curve register width");

static inline void write_pair(unsigned index, uint16_t low, uint16_t high)
{
    curve_register value = {.word = READ(index)};
    value.field.low = low;
    WRITE(index, value.word);
    value.word = READ(index);
    value.field.high = high;
    WRITE(index, value.word);
}

int gx_audio_in_set_fftvad_curve_1(uint16_t a, uint16_t b)
{
    if (a > 3072U || b > 17920U) return -1;
    write_pair(0x184U / 4U, a, b);
    return 0;
}

int gx_audio_in_set_fftvad_curve_2(uint16_t a, uint16_t b)
{
    if (a > 3072U || b > 7680U) return -1;
    write_pair(0x188U / 4U, a, b);
    return 0;
}

int gx_audio_in_set_fftvad_curve_3(int16_t a, int16_t b)
{
    if ((uint16_t)a > 4096U || (uint16_t)(b + 5120) > 10240U) return -1;
    write_pair(0x18CU / 4U, (uint16_t)a, (uint16_t)b);
    return 0;
}

int gx_audio_in_set_fftvad_curve_4(uint16_t a, uint16_t b)
{
    if (a > 5120U || b > 5120U) return -1;
    write_pair(0x190U / 4U, a, b);
    return 0;
}

int gx_audio_in_set_fftvad_curve_5(uint16_t a)
{
    if (a > 8192U) return -1;
    curve_register value = {.word = READ(0x194U / 4U)};
    value.field.low = a;
    WRITE(0x194U / 4U, value.word);
    return 0;
}
