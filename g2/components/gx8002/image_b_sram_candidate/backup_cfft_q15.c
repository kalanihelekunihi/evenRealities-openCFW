/* Loaded image B native 0x1000f1d4..0x1000f2b3.
 * Control dispatch matches pinned NationalChip csky_cfft_q15.c and native
 * branch destinations; butterfly and bit-reversal bodies stay explicit.
 */
#include "backup_fft_profile.h"

extern void gx8002_image_b_cfft_radix4_forward_1000f3fc(
    int16_t *data, uint32_t length, const int16_t *twiddle, uint32_t modifier);
extern void gx8002_image_b_cfft_radix4_inverse_1000f610(
    int16_t *data, uint32_t length, const int16_t *twiddle, uint32_t modifier);
extern void gx8002_image_b_cfft_radix4by2_forward_1000f2b4(
    int16_t *data, uint32_t length, const int16_t *twiddle);
extern void gx8002_image_b_cfft_radix4by2_inverse_1000f358(
    int16_t *data, uint32_t length, const int16_t *twiddle);
extern void gx8002_image_b_bit_reverse_1000f824(
    uint16_t *data, uint16_t length, const uint16_t *table);

void gx8002_image_b_cfft_q15_1000f1d4(
    const image_b_cfft_q15 *profile, int16_t *data, uint32_t inverse,
    uint32_t bit_reverse)
{
    uint32_t length = profile->length;
    if (inverse == 1u) {
        switch (length) {
        case 16: case 64: case 256: case 1024: case 4096:
            gx8002_image_b_cfft_radix4_inverse_1000f610(
                data, length, profile->twiddle, 1u);
            break;
        case 32: case 128: case 512: case 2048:
            gx8002_image_b_cfft_radix4by2_inverse_1000f358(
                data, length, profile->twiddle);
            break;
        default:
            break;
        }
    } else {
        switch (length) {
        case 16: case 64: case 256: case 1024: case 4096:
            gx8002_image_b_cfft_radix4_forward_1000f3fc(
                data, length, profile->twiddle, 1u);
            break;
        case 32: case 128: case 512: case 2048:
            gx8002_image_b_cfft_radix4by2_forward_1000f2b4(
                data, length, profile->twiddle);
            break;
        default:
            break;
        }
    }
    if (bit_reverse != 0u)
        gx8002_image_b_bit_reverse_1000f824(
            (uint16_t *)data, profile->bit_reverse_length,
            profile->bit_reverse_table);
}
