/* Main 0x481836 candidate: adapted from pinned IAR Bootloader source;
 * identical 1270-instruction core topology except 23 relocated BL sites. */
/* Reconstructed private AAPCS raw-word interfaces of the stock DP operations.
 */
#include <stdint.h>
/* Doubles travel as raw 64-bit words (the stock private ABI); the arithmetic
 * itself is ordinary VFP double arithmetic (round to nearest, truncating and
 * saturating integer conversion, as vcvt does). */
static inline double raw_to_double(uint64_t raw){double value;__builtin_memcpy(&value,&raw,sizeof value);return value;}
static inline uint64_t double_to_raw(double value){uint64_t raw;__builtin_memcpy(&raw,&value,sizeof raw);return raw;}
uint64_t g2_main_fp_mul(uint64_t x,uint64_t y){return double_to_raw(raw_to_double(x)*raw_to_double(y));}
uint64_t g2_main_fp_sub(uint64_t x,uint64_t y){return double_to_raw(raw_to_double(x)-raw_to_double(y));}
uint64_t g2_main_fp_div(uint64_t x,uint64_t y){return double_to_raw(raw_to_double(x)/raw_to_double(y));}
int32_t g2_main_fp_i32(uint64_t x){return (int32_t)raw_to_double(x);}
uint32_t g2_main_fp_u32(uint64_t x){return (uint32_t)raw_to_double(x);}
uint64_t g2_main_fp_from_i32(int32_t x){return double_to_raw((double)x);}
uint64_t g2_main_fp_from_u32(uint32_t x){return double_to_raw((double)x);}
uint64_t g2_main_fp_frexp(uint64_t x,int *exponent){
 uint64_t magnitude=x&UINT64_C(0x7fffffffffffffff);unsigned e=(unsigned)(magnitude>>52);
 if(!magnitude||e==0x7ff){*exponent=0;return x;}
 if(e){*exponent=(int)e-1022;return x-((uint64_t)(uint32_t)*exponent<<52);}
 unsigned high=(unsigned)(magnitude>>32),low=(unsigned)magnitude;unsigned shift=high?(unsigned)__builtin_clz(high)-11:(unsigned)__builtin_clz(low)+21;
 *exponent=-(int)shift-1021;return (x&UINT64_C(0x8000000000000000))+(magnitude<<shift)+UINT64_C(0x3fd0000000000000);
}
/* Stock 0x48262C (IAR printf x*10^n helper) */
uint64_t g2_main_fp_pow10(uint64_t x,unsigned exponent){uint64_t factor=UINT64_C(0x4024000000000000);while(exponent){if(exponent&1)x=g2_main_fp_mul(x,factor);factor=g2_main_fp_mul(factor,factor);exponent>>=1;}return x;}
