/* Loaded image B DSP leaves, native 0x1000f0c0, 0x1000f134,
 * 0x1000f180, and 0x1000f1ac.
 * Native pabs.s16.s saturates INT16_MIN to INT16_MAX, then pmax.u16
 * reduces every lane. The fill duplicates the low halfword across lanes.
 */
#include <stdint.h>

void gx8002_image_b_dsp_copy_1000f180(
    const int16_t *source, int16_t *destination, uint32_t count)
{
    /* Native ldbi/stbi walks forward, including for overlapping ranges. */
    for (uint32_t i = 0; i < count; ++i)
        destination[i] = source[i];
}

void gx8002_image_b_dsp_shift_1000f0c0(
    const int16_t *input, int32_t shift, int16_t *output, uint32_t count)
{
    for (uint32_t i = 0; i < count; ++i) {
        int32_t lane = input[i];
        if (shift >= 0) {
            int64_t scaled = shift >= 31 ?
                (lane > 0 ? INT64_MAX : lane < 0 ? INT64_MIN : 0) :
                (int64_t)lane * (INT64_C(1) << shift);
            output[i] = (int16_t)(scaled > 32767 ? 32767 :
                scaled < -32768 ? -32768 : scaled);
        } else {
            uint32_t amount = shift == INT32_MIN ? 31u : (uint32_t)-shift;
            /* A signed right shift of Q15 lanes rounds toward negative
             * infinity, as native pasr.s16 does. */
            int32_t divisor = amount >= 15u ? 32768 : (int32_t)(1u << amount);
            int32_t quotient = lane / divisor;
            if (lane < 0 && lane % divisor != 0)
                --quotient;
            output[i] = (int16_t)quotient;
        }
    }
}

void gx8002_image_b_dsp_peak_1000f134(
    const int16_t *input, int16_t *peak, uint32_t count)
{
    uint16_t maximum = 0;
    for (uint32_t i = 0; i < count; ++i) {
        int32_t lane = input[i];
        uint16_t magnitude = lane == -32768 ? 32767u :
            (uint16_t)(lane < 0 ? -lane : lane);
        if (magnitude > maximum)
            maximum = magnitude;
    }
    *peak = (int16_t)maximum;
}

void gx8002_image_b_dsp_clear_1000f1ac(
    uint32_t value, int16_t *destination, uint32_t count)
{
    int16_t lane = (int16_t)(uint16_t)value;
    for (uint32_t i = 0; i < count; ++i)
        destination[i] = lane;
}
