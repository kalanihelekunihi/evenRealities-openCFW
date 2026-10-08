/* Reconstructed private AAPCS raw-word interfaces of the stock DP operations.
 * Native VFP instructions retain rounding/exception semantics; LLVM software
 * arithmetic remains a separate compatibility lead, not silently substituted. */
#include <stdint.h>
#define BIN(name,op) __attribute__((naked)) uint64_t name(uint64_t x,uint64_t y){__asm__ volatile("vmov d0,r0,r1\nvmov d1,r2,r3\n" op " d0,d0,d1\nvmov r0,r1,d0\nbx lr\n");}
BIN(opencfw_fp_mul,"vmul.f64")
BIN(opencfw_fp_sub,"vsub.f64")
BIN(opencfw_fp_div,"vdiv.f64")
__attribute__((naked)) int32_t opencfw_fp_i32(uint64_t x){__asm__ volatile("vmov d0,r0,r1\nvcvt.s32.f64 s0,d0\nvmov r0,s0\nbx lr\n");}
__attribute__((naked)) uint32_t opencfw_fp_u32(uint64_t x){__asm__ volatile("vmov d0,r0,r1\nvcvt.u32.f64 s0,d0\nvmov r0,s0\nbx lr\n");}
__attribute__((naked)) uint64_t opencfw_fp_from_i32(int32_t x){__asm__ volatile("vmov s0,r0\nvcvt.f64.s32 d0,s0\nvmov r0,r1,d0\nbx lr\n");}
__attribute__((naked)) uint64_t opencfw_fp_from_u32(uint32_t x){__asm__ volatile("vmov s0,r0\nvcvt.f64.u32 d0,s0\nvmov r0,r1,d0\nbx lr\n");}
uint64_t opencfw_fp_frexp(uint64_t x,int *exponent){
 uint64_t magnitude=x&UINT64_C(0x7fffffffffffffff);unsigned e=(unsigned)(magnitude>>52);
 if(!magnitude||e==0x7ff){*exponent=0;return x;}
 if(e){*exponent=(int)e-1022;return x-((uint64_t)(uint32_t)*exponent<<52);}
 unsigned high=(unsigned)(magnitude>>32),low=(unsigned)magnitude;unsigned shift=high?(unsigned)__builtin_clz(high)-11:(unsigned)__builtin_clz(low)+21;
 *exponent=-(int)shift-1021;return (x&UINT64_C(0x8000000000000000))+(magnitude<<shift)+UINT64_C(0x3fd0000000000000);
}
uint64_t opencfw_fp_pow10(uint64_t x,unsigned exponent){uint64_t factor=UINT64_C(0x4024000000000000);while(exponent){if(exponent&1)x=opencfw_fp_mul(x,factor);factor=opencfw_fp_mul(factor,factor);exponent>>=1;}return x;}
