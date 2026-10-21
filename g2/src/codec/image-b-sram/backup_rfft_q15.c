/* Loaded image B, native 0x1000ef64..0x1000efd1.
 * Control flow and the five argument split ABI are checked against native
 * C-SKY instructions. This is the same Q15 RFFT algorithm and instance
 * layout as pinned NationalChip libdsp csky_rfft_q15.c (CMSIS/T-HEAD).
 * Its CFFT and split children remain independent source obligations.
 */
#include "backup_fft_profile.h"

extern void gx8002_image_b_cfft_q15_1000f1d4(
    const image_b_cfft_q15 *cfft, int16_t *data, uint32_t inverse,
    uint32_t bit_reverse);
extern void gx8002_image_b_split_rfft_q15_1000efd4(
    const int16_t *source, uint32_t half_length, const int16_t *twiddle,
    int16_t *destination, uint32_t modifier);
extern void gx8002_image_b_split_rifft_q15_1000f068(
    const int16_t *source, uint32_t half_length, const int16_t *twiddle,
    int16_t *destination, uint32_t modifier);

void gx8002_image_b_rfft_1000ef64(
    const image_b_rfft_q15 *profile, int16_t *source, int16_t *destination)
{
    const uint32_t half_length = profile->fft_len_real >> 1;
    if (profile->inverse == 1u) {
        gx8002_image_b_split_rifft_q15_1000f068(
            source, half_length, profile->twiddle_a, destination,
            profile->modifier);
        gx8002_image_b_cfft_q15_1000f1d4(
            profile->cfft, destination, profile->inverse,
            profile->bit_reverse);
        /* Native 0x1000efba..ce and the SDK's non-DSP3 path both shift
         * every Q15 output lane after inverse CFFT. */
        for (uint32_t i = 0; i < profile->fft_len_real; ++i)
            destination[i] = (int16_t)((uint16_t)destination[i] << 1);
    } else {
        gx8002_image_b_cfft_q15_1000f1d4(
            profile->cfft, source, profile->inverse, profile->bit_reverse);
        gx8002_image_b_split_rfft_q15_1000efd4(
            source, half_length, profile->twiddle_a, destination,
            profile->modifier);
    }
}
