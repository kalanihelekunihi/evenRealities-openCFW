/* Native image-B IMCRA process 0x10015d34..0x10015e36. This is an
 * independently reconstructed prefix, not the complete 0x10015d34 body.
 * It retains the overlap-save move, windowed Q15 input, zero tail,
 * peak normalization, forward RFFT and initial complex energy loop.
 */
#include <stdint.h>

extern void *gx8002_image_b_move_10009968(void *, const void *, uint32_t);
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern int gx8002_image_b_imcra_peak_shift_1000e2c4(const int16_t *, int);
extern void gx8002_image_b_imcra_block_scale_1000e28c(int16_t *, int, int);
extern void gx8002_image_b_rfft_1000ef64(
    const void *, int16_t *, int16_t *);

typedef struct {
    int32_t shift;
    float energy_scale;
} image_b_imcra_prefix_result;

static uint32_t field(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

image_b_imcra_prefix_result gx8002_image_b_imcra_process_prefix_chunk(
    uint8_t *state, const int16_t *input)
{
    uint32_t window_length = field(state, 0x0cu);
    uint32_t new_samples = field(state, 0x14u);
    int16_t *history = (int16_t *)(uintptr_t)field(state, 0x24u);
    uint32_t history_samples = window_length - new_samples;
    (void)gx8002_image_b_move_10009968(
        history, history + new_samples, history_samples * 2u);
    (void)gx8002_image_b_move_10009968(
        history + history_samples, input, new_samples * 2u);

    int16_t *window = (int16_t *)(uintptr_t)field(state, 0x30u);
    int16_t *work = (int16_t *)(uintptr_t)field(state, 0x38u);
    for (uint32_t i = 0; i < window_length; ++i) {
        int32_t product = (int32_t)history[i] * (int32_t)window[i];
        work[i] = (int16_t)(product >> 15);
    }
    uint32_t fft_length = field(state, 0x10u);
    gx8002_image_b_zero_100113c4(
        (void *)(work + window_length), 0u,
        (fft_length - window_length) * 2u);
    int32_t shift = gx8002_image_b_imcra_peak_shift_1000e2c4(
        work, (int32_t)field(state, 0x18u));
    if (shift < -9)
        shift = -9;
    gx8002_image_b_imcra_block_scale_1000e28c(
        work, (int32_t)field(state, 0x18u), shift);
    int16_t *fft_output = (int16_t *)(uintptr_t)field(state, 0x3cu);
    gx8002_image_b_rfft_1000ef64(
        (const void *)(uintptr_t)UINT32_C(0x20017020), work, fft_output);

    uint32_t scale_word = 1u;
    uint32_t shift_amount = (uint32_t)(shift + 9);
    __asm__ volatile("lsl %0, %1" : "+r"(scale_word) : "r"(shift_amount));
    float scale = (float)(int32_t)scale_word;
    float *energy = (float *)(uintptr_t)field(state, 0x40u);
    int32_t bins = (int32_t)field(state, 0x1cu);
    for (int32_t i = 0; i < bins; ++i) {
        float real = (float)fft_output[2 * i];
        float imag = (float)fft_output[2 * i + 1];
        volatile float imag_energy = imag * imag;
        imag_energy = imag_energy * scale;
        volatile float real_energy = real * real;
        real_energy = real_energy * scale;
        energy[i] = imag_energy + real_energy;
    }
    return (image_b_imcra_prefix_result){shift, scale};
}
