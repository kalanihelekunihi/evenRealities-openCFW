/* Native 0x1000f2b4 / 0x1000f358: pinned NationalChip Q15 radix-4-by-2.
 * Upstream Apache-2.0 copyright and license text is in the included file.
 */
#include <stdint.h>
extern void gx8002_image_b_cfft_radix4_forward_1000f3fc(
    int16_t *data, uint32_t length, int16_t *twiddle, uint32_t modifier);
extern void gx8002_image_b_cfft_radix4_inverse_1000f610(
    int16_t *data, uint32_t length, int16_t *twiddle, uint32_t modifier);
#define csky_radix4_butterfly_q15 gx8002_image_b_cfft_radix4_forward_1000f3fc
#define csky_radix4_butterfly_inverse_q15 gx8002_image_b_cfft_radix4_inverse_1000f610
#define csky_cfft_radix4by2_q15 gx8002_image_b_cfft_radix4by2_forward_1000f2b4
#define csky_cfft_radix4by2_inverse_q15 gx8002_image_b_cfft_radix4by2_inverse_1000f358
#include "../../../../third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source/TransformFunctions/csky_cfft_radix4by2_q15.c"
