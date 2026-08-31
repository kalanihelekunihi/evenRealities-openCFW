/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_MUSL_MATH_H
#define OPENCFW_MUSL_MATH_H

#include <float.h>

#if FLT_EVAL_METHOD == 0
typedef float float_t;
typedef double double_t;
#elif FLT_EVAL_METHOD == 1
typedef double float_t;
typedef double double_t;
#else
typedef long double float_t;
typedef long double double_t;
#endif

#define isnan(value) __builtin_isnan(value)
#define fabsf(value) __builtin_fabsf(value)
#define M_PI_2 1.570796326794896619231321691639751442

float acosf(float value);
float atan2f(float y, float x);
float atanf(float value);
float cosf(float value);
double floor(double value);
double fmod(double numerator, double denominator);
float fmodf(float numerator, float denominator);
float sinf(float value);
double sqrt(double value);
float sqrtf(float value);
double scalbn(double value, int exponent);
float tanf(float value);

#endif /* OPENCFW_MUSL_MATH_H */
