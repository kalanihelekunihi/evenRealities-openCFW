/* Authenticated loaded image-B Q15 descriptor fields.
 * Stock copies at 0x1001700c/20 have runtime aliases 0x2001700c/20.
 * The three coefficient tables are pinned NationalChip/CMSIS source data;
 * their source-owned target definitions and final placement remain separate.
 */
#include "backup_fft_profile.h"

extern const int16_t gx8002_image_b_real_coef_a_q15_512[512];
extern const int16_t gx8002_image_b_twiddle_coef_q15_256[384];
extern const uint16_t gx8002_image_b_bitrev_fixed_256[240];

static const image_b_cfft_q15 image_b_cfft_256 = {
    .length = 256,
    .reserved = 0,
    .twiddle = gx8002_image_b_twiddle_coef_q15_256,
    .bit_reverse_table = gx8002_image_b_bitrev_fixed_256,
    .bit_reverse_length = 240,
};

const image_b_rfft_q15 gx8002_image_b_rifft_profile_2001700c = {
    .fft_len_real = 512,
    .inverse = 1,
    .bit_reverse = 1,
    .reserved = {0, 0},
    .modifier = 1,
    .twiddle_a = gx8002_image_b_real_coef_a_q15_512,
    .cfft = &image_b_cfft_256,
};

const image_b_rfft_q15 gx8002_image_b_rfft_profile_20017020 = {
    .fft_len_real = 512,
    .inverse = 0,
    .bit_reverse = 1,
    .reserved = {0, 0},
    .modifier = 1,
    .twiddle_a = gx8002_image_b_real_coef_a_q15_512,
    .cfft = &image_b_cfft_256,
};
