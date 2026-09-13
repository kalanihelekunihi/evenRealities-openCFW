/* SPDX-License-Identifier: MIT */
/* Recovered Q15 real-FFT splitting, package 0x47914/0x479a8.
 * Candidate scalar implementation; preserve packed-lane negation in inverse.
 * Arithmetic right shifts and signed narrowing follow the C-SKY ABI.
 * Valid nonoverlapping buffers and coefficient indices are caller contracts. */
#include <stdint.h>
#include <limits.h>
static inline int32_t sat32(int64_t x) { return x>INT32_MAX?INT32_MAX:x<INT32_MIN?INT32_MIN:(int32_t)x; }
static __attribute__((noinline)) int32_t add_sat(int32_t x,int32_t y)
{
    uint32_t a=(uint32_t)x,b=(uint32_t)y,sum=a+b;
    /* Equal-sign operands overflow exactly when the sum changes sign. */
    if (((a^sum)&(b^sum))&0x80000000u) return x<0?INT32_MIN:INT32_MAX;
    return (int32_t)sum;
}
static int32_t wrap_sum(int32_t x,int32_t y) { return (int32_t)((uint32_t)x+(uint32_t)y); }
static int32_t wrap_sub(int32_t x,int32_t y) { return (int32_t)((uint32_t)x-(uint32_t)y); }
static int32_t complement_real(int32_t x)
{
    int32_t v=(int16_t)(uint16_t)(32768u-(uint32_t)x);
    return v==-32768?32767:v<0?-v:v;
}
#ifndef INVERSE
#define INVERSE 0
#endif
#if INVERSE
void open_cfw_gx8002_backup_split_inverse(int16_t *input,unsigned half,int16_t *coefficients,int16_t *output,unsigned modifier)
{
    for (unsigned i=0;i<half;i++) {
        int32_t ar=input[2*i],ai=input[2*i+1];
        int32_t br=input[2*(half-i)],bi=input[2*(half-i)+1];
        int32_t cr=coefficients[2*i*modifier],ci=coefficients[2*i*modifier+1];
        int32_t dr=complement_real(cr),di=(int16_t)(uint16_t)(0u-(uint32_t)ci);
        int32_t real=wrap_sub(br*dr,bi*di);
        int32_t imag=sat32((int64_t)br*di+(int64_t)bi*dr);
        real=add_sat(real,wrap_sum(ar*cr,ai*ci));
        /* Stock pneg.s16.s negates each halfword of the product independently. */
        int32_t lo=(int16_t)imag,hi=(int16_t)((uint32_t)imag>>16);
        lo=lo==-32768?32767:-lo;hi=hi==-32768?32767:-hi;
        imag=(int32_t)((uint32_t)(uint16_t)lo|((uint32_t)(uint16_t)hi<<16));
        imag=add_sat(imag,wrap_sub(cr*ai,ci*ar));
        output[2*i]=(int16_t)(real>>16);output[2*i+1]=(int16_t)(imag>>16);
    }
}
#else
void open_cfw_gx8002_backup_split_forward(int16_t *input,unsigned half,int16_t *coefficients,int16_t *output,unsigned modifier)
{
    for (unsigned i=1;i<half;i++) {
        int32_t ar=input[2*i],ai=input[2*i+1];
        int32_t br=input[2*(half-i)],bi=input[2*(half-i)+1];
        int32_t cr=coefficients[2*i*modifier],ci=coefficients[2*i*modifier+1];
        int32_t dr=complement_real(cr),di=(int16_t)(uint16_t)(0u-(uint32_t)ci);
        int32_t real=wrap_sub(ar*cr,ai*ci);
        int32_t imag=wrap_sub(br*di,bi*dr);
        real=add_sat(real,wrap_sum(br*dr,bi*di));
        imag=add_sat(imag,wrap_sum(ar*ci,ai*cr));
        output[2*i]=(int16_t)(real>>16);output[2*i+1]=(int16_t)(imag>>16);
    }
    int32_t real=input[0],imag=input[1];
    output[2*half]=(int16_t)((real-imag)>>1);output[2*half+1]=0;
    output[0]=(int16_t)((real+imag)>>1);output[1]=0;
}
#endif
