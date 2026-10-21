#ifndef GX8002_IMAGE_B_FFT_PROFILE_H
#define GX8002_IMAGE_B_FFT_PROFILE_H
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint16_t length;
    uint16_t reserved;
    const int16_t *twiddle;
    const uint16_t *bit_reverse_table;
    uint16_t bit_reverse_length;
} image_b_cfft_q15;

typedef struct {
    uint32_t fft_len_real;
    uint8_t inverse;
    uint8_t bit_reverse;
    uint8_t reserved[2];
    uint32_t modifier;
    const int16_t *twiddle_a;
    const image_b_cfft_q15 *cfft;
} image_b_rfft_q15;

_Static_assert(offsetof(image_b_cfft_q15, twiddle) == 4, "CFFT twiddle offset");
_Static_assert(offsetof(image_b_cfft_q15, bit_reverse_table) == 8, "CFFT bitrev offset");
_Static_assert(offsetof(image_b_cfft_q15, bit_reverse_length) == 12, "CFFT length offset");
_Static_assert(offsetof(image_b_rfft_q15, inverse) == 4, "RFFT flag offset");
_Static_assert(offsetof(image_b_rfft_q15, modifier) == 8, "RFFT modifier offset");
_Static_assert(offsetof(image_b_rfft_q15, twiddle_a) == 12, "RFFT table offset");
_Static_assert(offsetof(image_b_rfft_q15, cfft) == 16, "RFFT CFFT offset");
_Static_assert(sizeof(image_b_rfft_q15) == 20, "RFFT profile size");
_Static_assert(sizeof(image_b_cfft_q15) == 16, "CFFT profile size");

extern const image_b_rfft_q15 gx8002_image_b_rfft_profile_20017020;
extern const image_b_rfft_q15 gx8002_image_b_rifft_profile_2001700c;
#endif
