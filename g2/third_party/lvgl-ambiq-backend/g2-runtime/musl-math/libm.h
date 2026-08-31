/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_MUSL_LIBM_H
#define OPENCFW_MUSL_LIBM_H

#include <stdint.h>
#include <float.h>
#include "math.h"

#ifndef hidden
#define hidden __attribute__((visibility("hidden")))
#endif

#define WANT_ROUNDING 1
#define WANT_SNAN 0

#ifdef __GNUC__
#define predict_true(x) __builtin_expect(!!(x), 1)
#define predict_false(x) __builtin_expect(!!(x), 0)
#else
#define predict_true(x) (x)
#define predict_false(x) (x)
#endif

static inline void fp_force_evalf(float x)
{
    volatile float y = x;
    (void)y;
}

static inline void fp_force_eval(double x)
{
    volatile double y = x;
    (void)y;
}

static inline void fp_force_evall(long double x)
{
    volatile long double y = x;
    (void)y;
}

static inline double eval_as_double(double x)
{
    double y = x;
    return y;
}

#define FORCE_EVAL(x) do {                        \
    if(sizeof(x) == sizeof(float)) fp_force_evalf(x); \
    else if(sizeof(x) == sizeof(double)) fp_force_eval(x); \
    else fp_force_evall(x);                       \
} while(0)

#define asuint(value) ((union { float _f; uint32_t _i; }){value})._i
#define asfloat(word) ((union { uint32_t _i; float _f; }){word})._f
#define asuint64(value) ((union { double _f; uint64_t _i; }){value})._i
#define asdouble(word) ((union { uint64_t _i; double _f; }){word})._f

#define GET_FLOAT_WORD(word, value) do { (word) = asuint(value); } while(0)
#define SET_FLOAT_WORD(value, word) do { (value) = asfloat(word); } while(0)

hidden int __rem_pio2_large(double *, double *, int, int, int);
hidden int __rem_pio2f(float, double *);
hidden float __sindf(double);
hidden float __cosdf(double);
hidden float __tandf(double, int);
hidden double __math_invalid(double);

#endif /* OPENCFW_MUSL_LIBM_H */
