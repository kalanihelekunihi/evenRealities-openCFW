/* SPDX-License-Identifier: MIT */
#include "newlib_double_compat.h"
#if !defined(__BYTE_ORDER__) || __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "Gx8002 reduction adapter requires little endian"
#endif
#define GET_HIGH_WORD(hi,x) do { union { double d; uint64_t u; } w_={.d=(x)}; (hi)=(uint32_t)(w_.u>>32); } while(0)
#define GET_LOW_WORD(lo,x) do { union { double d; uint64_t u; } w_={.d=(x)}; (lo)=(uint32_t)w_.u; } while(0)
/* Write only the selected object bytes. The reducer initializes z with two
 * consecutive word setters; reading all of z in the first setter is invalid. */
#define OPEN_CFW_SET_WORD(x,word,offset) do { uint32_t v_=(uint32_t)(word); unsigned char *p_=(unsigned char *)&(x)+(offset); p_[0]=(unsigned char)v_; p_[1]=(unsigned char)(v_>>8); p_[2]=(unsigned char)(v_>>16); p_[3]=(unsigned char)(v_>>24); } while(0)
#define SET_LOW_WORD(x,word) OPEN_CFW_SET_WORD(x,word,0)
#define SET_HIGH_WORD(x,word) OPEN_CFW_SET_WORD(x,word,4)
double fabs(double);
double scalbn(double,int);
double floor(double);
int __kernel_rem_pio2(double *,double *,int,int,int,const __int32_t *);
