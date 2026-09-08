/* SPDX-License-Identifier: MIT */
/* Recovered GX8002 audio-in register leaves. Unlike the analog flags,
 * these inputs are masked to the exact hardware field width by INS.
 */
#include <stdint.h>
#if defined(OPEN_CFW_GX8002_I2S_HOST_TEST)
extern volatile uint32_t open_cfw_gx8002_i2s_registers[3];
#define AUDIO_WORD(index) open_cfw_gx8002_i2s_registers[index]
#else
#define AUDIO_WORD(index) (((volatile uint32_t *)0xA0A00000U)[index])
#endif

typedef union {
    uint32_t word;
    struct { uint32_t low : 24, value : 3, high : 5; } clock;
    struct { uint32_t low : 16, value : 1, high : 15; } input;
    struct { uint32_t low : 4, value : 1, high : 27; } output;
} audio_register;
/* Bitfield allocation is implementation-defined. Target instruction comparison
 * is mandatory; these local fields are never used as volatile MMIO objects. */
_Static_assert(sizeof(audio_register) == sizeof(uint32_t), "audio register width");

int gx_audio_in_set_i2s_clock(uint32_t value)
{
    audio_register register_value = {.word = AUDIO_WORD(0)};
    register_value.clock.value = value;
    AUDIO_WORD(0) = register_value.word;
    return 0;
}

int gx_audio_in_set_i2sin_mode(uint32_t value)
{
    audio_register register_value = {.word = AUDIO_WORD(1)};
    register_value.input.value = value;
    AUDIO_WORD(1) = register_value.word;
    return 0;
}

int gx_audio_in_set_i2sout_mode(uint32_t value)
{
    audio_register register_value = {.word = AUDIO_WORD(2)};
    register_value.output.value = value;
    AUDIO_WORD(2) = register_value.word;
    return 0;
}
