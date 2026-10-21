/* Native image-B 0x10010ca4, source-attributed to Sun fdlibm
 * k_rem_pio2.c in pinned Android bionic a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349.
 * Full body is included as C from the pinned source. Copyright (C) 1993
 * Sun Microsystems, Inc.; developed at SunSoft. Permission to use, copy,
 * modify and distribute is freely granted with this notice preserved.
 */
#include <stdint.h>
#include <math.h>
#define lint 1
#define _MATH_PRIVATE_H_
extern double gx8002_image_b_scalbn_double(double x, int exponent);
extern double gx8002_image_b_floor_double(double x);
#define scalbn gx8002_image_b_scalbn_double
#define floor gx8002_image_b_floor_double
#define __kernel_rem_pio2 gx8002_image_b_kernel_rem_pio2_10010ca4
#include "../../../../third-party/upstream/android-bionic-fdlibm-a27d2baa/libm/src/k_rem_pio2.c"
#undef __kernel_rem_pio2
#undef floor
#undef scalbn
