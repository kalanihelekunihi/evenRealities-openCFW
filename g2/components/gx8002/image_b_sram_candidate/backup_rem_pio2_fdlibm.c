/* Native 0x1000fcfc, source-attributed to Sun fdlibm e_rem_pio2.c in
 * pinned Android bionic a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349.
 * The full C body stays in the pinned repository. This wrapper supplies
 * C-SKY little-endian word accessors and source-owned symbol relocations.
 * Copyright (C) 1993 Sun Microsystems, Inc. All rights reserved.
 * Developed at SunSoft. Permission to use, copy, modify and distribute is
 * freely granted provided this notice is preserved.
 */
#include <stdint.h>
#include <math.h>
#define lint 1
#define _MATH_PRIVATE_H_
#define u_int32_t uint32_t
extern int gx8002_image_b_kernel_rem_pio2_10010ca4(
    double *x, double *y, int e0, int nx, int precision, const int32_t *ipio2);
extern double gx8002_image_b_fabs_double_1000fc58(double x);
#define __kernel_rem_pio2 gx8002_image_b_kernel_rem_pio2_10010ca4
#define fabs gx8002_image_b_fabs_double_1000fc58
#define __ieee754_rem_pio2 gx8002_image_b_reduce_pi_over_two_1000fcfc
#include "../../../../third-party/upstream/android-bionic-fdlibm-a27d2baa/libm/src/e_rem_pio2.c"
#undef __ieee754_rem_pio2
#undef fabs
#undef __kernel_rem_pio2
