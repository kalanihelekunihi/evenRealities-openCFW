/* Native image-B 0x10010f50 and 0x1001106c. Direct Sun fdlibm kernel
 * polynomials from pinned Android bionic libm/src/k_sin.c and k_cos.c,
 * commit a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349.
 * Copyright (C) 1993 Sun Microsystems, Inc. All rights reserved.
 * Developed at SunSoft. Permission to use, copy, modify and distribute is
 * freely granted provided this notice is preserved.
 */

double gx8002_image_b_kernel_sin_10010f50(double x, double y, int tail)
{
    const double half = 5.00000000000000000000e-01;
    /* Stock 0x10011012 materializes +0x3fc5555555555554 and subtracts
     * its product. This differs from the upstream fdlibm S1 coefficient. */
    const double s1 = -0x1.5555555555554p-3;
    const double s2 =  8.33333333332248946124e-03;
    const double s3 = -1.98412698298579493134e-04;
    const double s4 =  2.75573137070700676789e-06;
    const double s5 = -2.50507602534068634195e-08;
    const double s6 =  1.58969099521155010221e-10;
    double z = x * x;
    double v = z * x;
    double r = s2 + z * (s3 + z * (s4 + z * (s5 + z * s6)));
    if (tail == 0) return x + v * (s1 + z * r);
    return x - ((z * (half * y - v * r) - y) - v * s1);
}

double gx8002_image_b_kernel_cos_1001106c(double x, double y)
{
    const double c1 =  4.16666666666666019037e-02;
    const double c2 = -1.38888888888741095749e-03;
    const double c3 =  2.48015872894767294178e-05;
    const double c4 = -2.75573143513906633035e-07;
    const double c5 =  2.08757232129817482790e-09;
    const double c6 = -1.13596475577881948265e-11;
    double z = x * x;
    double r = z * (c1 + z * (c2 + z * (c3 + z * (c4 + z * (c5 + z * c6)))));
    double hz = (float)0.5 * z;
    double w = 1.0 - hz;
    return w + (((1.0 - w) - hz) + (z * r - x * y));
}
