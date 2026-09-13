/* SPDX-License-Identifier: MIT */
/* Binary32 ABI adapter for pinned Newlib algorithms; no firmware data. */
#include <stdint.h>
#include <float.h>
typedef int32_t __int32_t;
typedef uint32_t __uint32_t;
_Static_assert(FLT_RADIX == 2 && FLT_MANT_DIG == 24 && FLT_MAX_EXP == 128, "binary32 required");
#define GET_FLOAT_WORD(i,x) do { union {float f; uint32_t u;} word_ = {.f=(x)}; (i)=word_.u; } while (0)
#define SET_FLOAT_WORD(x,i) do { union {float f; uint32_t u;} word_ = {.u=(uint32_t)(i)}; (x)=word_.f; } while (0)
#define FLT_UWORD_IS_FINITE(x) ((x)<0x7f800000L)
#define FLT_UWORD_IS_NAN(x) ((x)>0x7f800000L)
#define FLT_UWORD_IS_INFINITE(x) ((x)==0x7f800000L)
#define FLT_UWORD_IS_ZERO(x) ((x)==0)
#define FLT_UWORD_IS_SUBNORMAL(x) ((x)<0x00800000L)
#define FLT_UWORD_EXP_MAX 0x43000000
#define FLT_UWORD_EXP_MIN 0x43160000
float __ieee754_sqrtf(float);
float open_cfw_gx8002_float_absolute(float);
float open_cfw_gx8002_scale_float(float,int);
static inline float open_cfw_math_nan(const char *tag) { (void)tag; return __builtin_nanf(""); }
#define fabsf open_cfw_gx8002_float_absolute
#define scalbnf open_cfw_gx8002_scale_float
#define nanf open_cfw_math_nan
