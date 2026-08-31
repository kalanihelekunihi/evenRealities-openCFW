/* SPDX-License-Identifier: MIT */
/* Public exact-symbol wrappers around the pinned musl scalar math closure. */

#include "musl-math/math.h"

#define OPEN_CFW_PUBLIC __attribute__((visibility("default"), used, noinline))
#define OPEN_CFW_HIDDEN __attribute__((visibility("hidden")))

extern OPEN_CFW_HIDDEN float open_cfw_musl_acosf(float);
extern OPEN_CFW_HIDDEN float open_cfw_musl_atan2f(float, float);
extern OPEN_CFW_HIDDEN float open_cfw_musl_atanf(float);
extern OPEN_CFW_HIDDEN double open_cfw_musl_fmod(double, double);
extern OPEN_CFW_HIDDEN float open_cfw_musl_fmodf(float, float);

OPEN_CFW_HIDDEN float open_cfw_musl_sqrtf(float value)
{
#if defined(__arm__) || defined(__thumb__)
    float result;
    __asm__ volatile("vsqrt.f32 %0, %1" : "=t"(result) : "t"(value));
    return result;
#else
    return __builtin_sqrtf(value);
#endif
}

OPEN_CFW_PUBLIC float acosf(float value) { return open_cfw_musl_acosf(value); }
OPEN_CFW_PUBLIC float atan2f(float y, float x) { return open_cfw_musl_atan2f(y, x); }
OPEN_CFW_PUBLIC float atanf(float value) { return open_cfw_musl_atanf(value); }
OPEN_CFW_PUBLIC double fmod(double x, double y) { return open_cfw_musl_fmod(x, y); }
OPEN_CFW_PUBLIC float fmodf(float x, float y) { return open_cfw_musl_fmodf(x, y); }
