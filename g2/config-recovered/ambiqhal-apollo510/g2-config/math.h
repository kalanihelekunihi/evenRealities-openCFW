/* Compat: minimal <math.h> for the freestanding AmbiqSuite 5.1.0 HAL units
 * (am_hal_syspll.c, am_hal_i2s.c). Declarations only; the single-precision
 * bodies are the reconstructed stock runtime (g2/src/apollo-main/runtime/
 * float-runtime) bound by the payload defsym map. Not a vendor file. */
#ifndef G2_AMBIQHAL_COMPAT_MATH_H
#define G2_AMBIQHAL_COMPAT_MATH_H
float floorf(float x);
float ceilf(float x);
float roundf(float x);
float fmodf(float x, float y);
float fabsf(float x);
double floor(double x);
double ceil(double x);
double round(double x);
double fmod(double x, double y);
double fabs(double x);
#endif
