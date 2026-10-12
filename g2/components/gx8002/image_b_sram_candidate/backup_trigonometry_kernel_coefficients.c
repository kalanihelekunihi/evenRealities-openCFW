/* Native normal-copy 0x10017034..0x1001708b -> 0x20017034..0x2001708b.
 * Eleven binary64 kernel coefficients from pinned Android bionic fdlibm
 * commit a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349,
 * libm/src/k_sin.c S2..S6 and libm/src/k_cos.c C1..C6. Stock ordering and
 * addresses are authenticated; this typed source is an unselected placement
 * candidate pending complete normal-copy/CRT integration. */
#include <stdint.h>

typedef struct {
    double sine_s2, sine_s3, sine_s4, sine_s5, sine_s6;
    double cosine_c1, cosine_c2, cosine_c3, cosine_c4, cosine_c5, cosine_c6;
} image_b_kernel_coefficients;

_Static_assert(sizeof(image_b_kernel_coefficients) == 88,
               "native kernel coefficient extent");

const image_b_kernel_coefficients
gx8002_image_b_kernel_coefficients_20017034
    __attribute__((section(".data.image_b.kernel_coefficients"), used)) = {
        .sine_s2   =  8.33333333332248946124e-03,
        .sine_s3   = -1.98412698298579493134e-04,
        .sine_s4   =  2.75573137070700676789e-06,
        .sine_s5   = -2.50507602534068634195e-08,
        .sine_s6   =  1.58969099521155010221e-10,
        .cosine_c1 =  4.16666666666666019037e-02,
        .cosine_c2 = -1.38888888888741095749e-03,
        .cosine_c3 =  2.48015872894767294178e-05,
        .cosine_c4 = -2.75573143513906633035e-07,
        .cosine_c5 =  2.08757232129817482790e-09,
        .cosine_c6 = -1.13596475577881948265e-11,
    };
