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

/* IAR's private binary exponent scaler, reached through the raw-word wrapper
 * at 0x422700. The error cell is the literal used by its native out-of-line
 * error writer at 0x4275d2; this is RAM state, not a replacement policy. */
uint64_t opencfw_fp_scale2(uint64_t x,int32_t scale){
 uint32_t hi=(uint32_t)(x>>32),lo=(uint32_t)x;
 uint32_t e=(hi>>20)&0x7ffu,n=(uint32_t)scale;
 if(scale>=0){
  if(e==0x7ffu)return x;
  if(e){
   uint32_t sum=e+n;
   if(sum<0x7ffu)return x+((uint64_t)n<<52);
   *(volatile uint32_t *)(uintptr_t)0x20027194=34;
   return ((uint64_t)(hi&0x80000000u|0x7ff00000u)<<32);
  }
  if(!(lo|(hi<<1)))return x;
  if(n<1020u)return opencfw_fp_mul(x,(uint64_t)(n+1023u)<<52);
  x=opencfw_fp_mul(x,UINT64_C(0x7f00000000000000));
  hi=(uint32_t)(x>>32);e=(hi>>20)&0x7ffu;
  n-=1016u;
  if(e+n+1u<0x7ffu)return x+((uint64_t)n<<52);
  *(volatile uint32_t *)(uintptr_t)0x20027194=34;
  return ((uint64_t)(hi&0x80000000u|0x7ff00000u)<<32);
 }
 n=0u-n;
 if(e==0x7ffu)return x;
 if(e&&n<e)return x-((uint64_t)n<<52);
 if(e){uint32_t decrement=e-1u;n-=decrement;x-=((uint64_t)decrement<<52);}
 else if(!(lo|(hi<<1)))return x;
 if(n>=55u){*(volatile uint32_t *)(uintptr_t)0x20027194=34;return x&UINT64_C(0x8000000000000000);}
 uint32_t fpscr,before,after;
 __asm__ volatile("vmrs %0,fpscr":"=r"(before));
 fpscr=before&~UINT32_C(0x1f1f);
 __asm__ volatile("vmsr fpscr,%0"::"r"(fpscr):"memory");
 uint64_t result=opencfw_fp_mul(x,(uint64_t)(1023u-n)<<52);
 __asm__ volatile("vmrs %0,fpscr":"=r"(after));
 __asm__ volatile("vmsr fpscr,%0"::"r"(before):"memory");
 if(after&8u)*(volatile uint32_t *)(uintptr_t)0x20027194=34;
 return result;
}
