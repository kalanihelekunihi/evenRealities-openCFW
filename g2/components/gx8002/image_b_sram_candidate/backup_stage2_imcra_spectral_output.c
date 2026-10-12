/* Image-B IMCRA 0x10016404..0x1001651a: gain-applied inverse RFFT,
 * overlap-add output, residual refresh, and frame-count increment.
 * The complete provider still needs preceding adaptive control flow.
 */
#include <stdint.h>

extern int gx8002_image_b_imcra_peak_shift_1000e2c4(const int16_t *, int);
extern void gx8002_image_b_imcra_block_scale_1000e28c(int16_t *, int, int);
extern void gx8002_image_b_rfft_1000ef64(
    const void *, int16_t *, int16_t *);

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

static int16_t native_q15(int16_t left, int16_t right)
{
    int32_t product = (int32_t)left * (int32_t)right;
    return (int16_t)(product >> 15);
}

static int32_t native_extract_29_14(uint32_t value)
{
    return (int32_t)(value << 2) >> 16;
}

void gx8002_image_b_imcra_spectral_output_chunk(
    uint8_t *state, int16_t *output, int32_t forward_shift)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    int16_t *spectrum = (int16_t *)(uintptr_t)word(state, 0x3cu);
    const float *gain = (const float *)(uintptr_t)word(state, 0x44u);
    for (int32_t i = 0; i < bins; ++i) {
        spectrum[2 * i] = (int16_t)(int32_t)((float)spectrum[2 * i] * gain[i]);
        spectrum[2 * i + 1] =
            (int16_t)(int32_t)((float)spectrum[2 * i + 1] * gain[i]);
    }
    int32_t fft_count = (int32_t)word(state, 0x18u);
    int32_t inverse_shift = gx8002_image_b_imcra_peak_shift_1000e2c4(
        spectrum, fft_count + 2);
    gx8002_image_b_imcra_block_scale_1000e28c(
        spectrum, fft_count + 2, inverse_shift);
    int16_t *work = (int16_t *)(uintptr_t)word(state, 0x38u);
    gx8002_image_b_rfft_1000ef64(
        (const void *)(uintptr_t)UINT32_C(0x2001700c), spectrum, work);
    gx8002_image_b_imcra_block_scale_1000e28c(
        work, fft_count, -9 - forward_shift - inverse_shift);

    int32_t fresh = (int32_t)word(state, 0x14u);
    int32_t window_length = (int32_t)word(state, 0x0cu);
    const int16_t *window = (const int16_t *)(uintptr_t)word(state, 0x30u);
    int16_t *residual = (int16_t *)(uintptr_t)word(state, 0x2cu);
    const int16_t *output_window =
        (const int16_t *)(uintptr_t)word(state, 0x34u);
    for (int32_t i = 0; i < fresh; ++i) {
        int32_t sum = (int32_t)native_q15(window[i], work[i]) +
                      (int32_t)residual[i];
        /* Native mulsh consumes the low signed halfwords of both registers.
         * The overlap sum can exceed int16_t; its low halfword is selected
         * before the output-window product. */
        uint32_t product =
            (uint32_t)((int32_t)(int16_t)sum * (int32_t)output_window[i]);
        int32_t sample = native_extract_29_14(product);
        if (sample < -32767)
            sample = -32767;
        output[i] = (int16_t)sample;
    }
    for (int32_t i = fresh; i < window_length; ++i)
        residual[i - fresh] = native_q15(window[i], work[i]);
    *(uint32_t *)(void *)(state + 0x20u) = word(state, 0x20u) + 1u;
}
