/* Native image-B 0x1000e94c..0x1000ea5e, FrameDrcProcess.
 * The float gain arrives in FR0, matching the caller's fsitos conversion.
 * The native widening/absolute/narrowing child chain is exact for finite
 * binary32 inputs when expressed as a sign-bit clear on the original word.
 * The two FPU accumulate forms follow pinned C-SKY QEMU fmacs/fmscs.
 * Finite-output byte
 * equality and hardware rounding remain separate qualification gates.
 */
#include <stdint.h>

extern float gx8002_image_b_power_float_100100a4(float, float);

typedef union { float value; uint32_t bits; } binary32;

static float native_magnitude(float input)
{
    binary32 number = {.value = input};
    number.bits &= UINT32_C(0x7fffffff);
    return number.value;
}

void gx8002_image_b_drc_process_1000e94c(
    const uint32_t *state, int16_t *samples, float gain_db)
{
    float gain = gx8002_image_b_power_float_100100a4(
        10.0f, gain_db / 20.0f);
    int32_t length = (int32_t)state[1];
    if (length <= 0)
        return;
    float maximum = 0.0f;
    for (int32_t index = 0; index < length; ++index) {
        float scaled = (float)samples[index] * gain;
        float magnitude = native_magnitude(scaled);
        if (!(magnitude < maximum))
            maximum = magnitude;
    }
    maximum -= 30000.0f;
    float ratio = maximum >= 0.0f ? 2000.0f / maximum : 1.0f;
    for (int32_t index = 0; index < length; ++index) {
        float scaled = (float)samples[index] * gain;
        float output;
        if (scaled > 30000.0f) {
            float excess = scaled - 30000.0f;
            output = 30000.0f + excess * ratio;
        } else if (scaled < -30000.0f) {
            float excess = scaled + 30000.0f;
            output = excess * ratio - 30000.0f;
        } else {
            output = scaled;
        }
        samples[index] = (int16_t)(int32_t)output;
    }
}
