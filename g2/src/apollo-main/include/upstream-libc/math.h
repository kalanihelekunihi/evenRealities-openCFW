/* SPDX-License-Identifier: MIT
 * Freestanding <math.h> for pinned upstream units in the G2 Apollo main
 * image (cJSON). Hard-float calling convention, as stock.
 */
#ifndef G2_UPSTREAM_LIBC_MATH_H
#define G2_UPSTREAM_LIBC_MATH_H
double fabs(double value);
double floor(double value);
double pow(double base, double exponent);
#define isnan(x) __builtin_isnan(x)
#define isinf(x) __builtin_isinf(x)
#endif
