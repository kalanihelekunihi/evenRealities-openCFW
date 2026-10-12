/* Image-B native 0x1000d2a4..0x1000d467, frame transform orchestration.
 * Context offsets and call order follow the retained instruction/decompiler
 * body. The C-SKY DSP and FFT children are genuine separately unowned code.
 * Product RFFT profile at 0x20017020 remains initialized-data/linker input.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>
#include <stddef.h>
#include "backup_fft_profile.h"

extern void gx8002_image_b_dsp_peak_1000f134(
    const int16_t *input, int16_t *peak, uint32_t count);
extern void gx8002_image_b_dsp_shift_1000f0c0(
    const int16_t *input, int32_t shift, int16_t *scratch, uint32_t count);
extern void gx8002_image_b_dsp_clear_1000f1ac(
    uint32_t value, int16_t *destination, uint32_t count);
extern void gx8002_image_b_rfft_1000ef64(
    const image_b_rfft_q15 *profile, int16_t *scratch, int16_t *output);

static int32_t field_i32(const uint8_t *base, uint32_t offset)
{
    return *(const int32_t *)(const void *)(base + offset);
}
static uintptr_t field_address(const uint8_t *base, uint32_t offset)
{
    return (uintptr_t)*(const uint32_t *)(const void *)(base + offset);
}

uint32_t gx8002_image_b_dsp_transform_1000d2a4(
    const void *context, void *samples, uint32_t phase_word)
{
    const uint8_t *ctx = (const uint8_t *)context;
    int32_t rows = field_i32(ctx, 4u);
    int32_t bins = field_i32(ctx, 12u);
    int32_t phases = field_i32(ctx, 8u);
    int32_t phase = (int32_t)phase_word % phases;
    int32_t padded_bins = field_i32(ctx, 20u);
    int32_t phase_stride = field_i32(ctx, 24u);
    int16_t *scratch = (int16_t *)field_address(ctx, 0x84u);
    int16_t peak = 0;
    gx8002_image_b_dsp_peak_1000f134(
        (const int16_t *)samples, &peak, (uint32_t)bins * (uint32_t)rows);

    uint16_t magnitude = (uint16_t)peak;
    uint16_t shift = 15u;
    for (int bit = 14; bit >= 0; --bit) {
        if ((magnitude & (uint16_t)(1u << bit)) != 0u) {
            shift = (uint16_t)(14 - bit);
            break;
        }
    }
    int16_t *shift_slot = (int16_t *)field_address(ctx, 0x94u);
    shift_slot[phase] = (int16_t)shift;

    if (rows > 0) {
        int16_t *input = (int16_t *)samples;
        for (int32_t row = 0; row < rows; ++row) {
            uintptr_t output_base = field_address(
                ctx, row == 0 ? 0x78u : 0x7cu);
            gx8002_image_b_dsp_shift_1000f0c0(
                input, (int32_t)(int8_t)shift, scratch, (uint32_t)bins);

            int32_t active_bins = field_i32(ctx, 12u);
            if (active_bins > 0) {
                const int32_t *weights =
                    (const int32_t *)field_address(ctx, 0x70u);
                for (int32_t j = 0; j < active_bins; ++j) {
                    uint32_t product = (uint32_t)weights[j] *
                        (uint32_t)(int32_t)scratch[j];
                    scratch[j] = (int16_t)((int32_t)product >> 15);
                }
            }
            gx8002_image_b_dsp_clear_1000f1ac(
                0u, scratch + bins, (uint32_t)(padded_bins - bins));
            gx8002_image_b_rfft_1000ef64(
                &gx8002_image_b_rfft_profile_20017020, scratch,
                (int16_t *)(output_base +
                    (uintptr_t)phase * (uintptr_t)phase_stride * 4u));
            input += bins;
        }
    }
    return 0u;
}
