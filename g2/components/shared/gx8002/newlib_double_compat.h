/* SPDX-License-Identifier: MIT */
/* Binary64 word adapter for unchanged pinned Newlib algorithms. */
#include <stdint.h>
#include <float.h>
typedef int32_t __int32_t;
typedef uint32_t __uint32_t;
_Static_assert(sizeof(double)==8 && FLT_RADIX==2 && DBL_MANT_DIG==53 && DBL_MAX_EXP==1024,"binary64 required");
#define EXTRACT_WORDS(hi,lo,x) do { union { double d; uint64_t u; } w_={.d=(x)}; (hi)=(uint32_t)(w_.u>>32); (lo)=(uint32_t)w_.u; } while(0)
#define INSERT_WORDS(x,hi,lo) do { union { double d; uint64_t u; } w_={.u=((uint64_t)(uint32_t)(hi)<<32)|(uint32_t)(lo)}; (x)=w_.d; } while(0)
