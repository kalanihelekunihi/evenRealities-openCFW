/* SPDX-License-Identifier: MIT */
/* Scalar recovery of the backup Q15 radix-4 stages, package 0x47d3c/0x47f50.
 * Candidate: valid powers of four >=16, disjoint sample/coefficient arrays.
 * Stage-specific saturation and half shifts follow the decoded packed DSP.
 * Signed right shifts require the target compiler's arithmetic convention. */
#include <stdint.h>
#include <limits.h>
typedef struct { int32_t real,imag; } complex_q15;
static int32_t sat16(int32_t x) { return x>32767?32767:x< -32768?-32768:x; }
static complex_q15 load(const int16_t *p) { return (complex_q15){p[0],p[1]}; }
static void store(int16_t *p,complex_q15 a) { p[0]=(int16_t)a.real;p[1]=(int16_t)a.imag; }
static complex_q15 shift(complex_q15 a,unsigned n) { return (complex_q15){a.real>>n,a.imag>>n}; }
static complex_q15 add(complex_q15 a,complex_q15 b) { return (complex_q15){sat16(a.real+b.real),sat16(a.imag+b.imag)}; }
static complex_q15 sub(complex_q15 a,complex_q15 b) { return (complex_q15){sat16(a.real-b.real),sat16(a.imag-b.imag)}; }
static complex_q15 half_add(complex_q15 a,complex_q15 b) { return (complex_q15){(a.real+b.real)>>1,(a.imag+b.imag)>>1}; }
static complex_q15 half_sub(complex_q15 a,complex_q15 b) { return (complex_q15){(a.real-b.real)>>1,(a.imag-b.imag)>>1}; }
#ifndef INVERSE
#define INVERSE 0
#endif
/* First-stage crossed arithmetic saturates; later stages halve without saturation. */
static complex_q15 cross(complex_q15 a,complex_q15 b,unsigned plus,unsigned halve)
{
    int32_t x=plus?a.real+b.imag:a.real-b.imag;
    int32_t y=plus?a.imag-b.real:a.imag+b.real;
    return halve?(complex_q15){x>>1,y>>1}:(complex_q15){sat16(x),sat16(y)};
}
static int32_t sat_sum_products(int32_t a,int32_t b)
{
    /* Each argument is a signed Q15 product. The only overflowing sum
     * is two (-32768 * -32768) products; all other sums fit int32_t. */
    if (a==1073741824 && b==1073741824) return INT32_MAX;
    return (int32_t)((uint32_t)a+(uint32_t)b);
}
static complex_q15 multiply(complex_q15 value,complex_q15 coefficient)
{
    int32_t real,imag;
#if INVERSE
    real=(int32_t)((uint32_t)(coefficient.real*value.real)-(uint32_t)(coefficient.imag*value.imag));
    imag=sat_sum_products(coefficient.real*value.imag,coefficient.imag*value.real);
#else
    real=sat_sum_products(coefficient.real*value.real,coefficient.imag*value.imag);
    imag=(int32_t)((uint32_t)(coefficient.real*value.imag)-(uint32_t)(coefficient.imag*value.real));
#endif
    return (complex_q15){real>>16,imag>>16};
}
#if INVERSE
#define ENTRY open_cfw_gx8002_backup_radix4_inverse
#else
#define ENTRY open_cfw_gx8002_backup_radix4
#endif
void ENTRY(int16_t *samples,unsigned length,const int16_t *coefficients,unsigned modifier)
{
    unsigned quarter=length>>2;
    for (unsigned i=0;i<quarter;i++) {
        complex_q15 a=shift(load(samples+2*i),2),b=shift(load(samples+2*(i+quarter)),2);
        complex_q15 c=shift(load(samples+2*(i+2*quarter)),2),d=shift(load(samples+2*(i+3*quarter)),2);
        complex_q15 ac=add(a,c),bd=add(b,d),ac_diff=sub(a,c),bd_diff=sub(b,d);
        unsigned k=i*modifier;
        store(samples+2*i,half_add(ac,bd));
        store(samples+2*(i+quarter),multiply(sub(ac,bd),load(coefficients+4*k)));
        store(samples+2*(i+2*quarter),multiply(cross(ac_diff,bd_diff,!INVERSE,0),load(coefficients+2*k)));
        store(samples+2*(i+3*quarter),multiply(cross(ac_diff,bd_diff,INVERSE,0),load(coefficients+6*k)));
    }
    modifier*=4;
    for (unsigned group=quarter;group>4;group>>=2) {
        quarter>>=2;
        for (unsigned j=0;j<quarter;j++) {
            unsigned k=j*modifier;
            complex_q15 w1=load(coefficients+2*k),w2=load(coefficients+4*k),w3=load(coefficients+6*k);
            for (unsigned i=j;i<length;i+=group) {
                complex_q15 a=load(samples+2*i),b=load(samples+2*(i+quarter));
                complex_q15 c=load(samples+2*(i+2*quarter)),d=load(samples+2*(i+3*quarter));
                complex_q15 ac=add(a,c),bd=add(b,d),ac_diff=sub(a,c),bd_diff=sub(b,d);
                store(samples+2*i,shift(half_add(ac,bd),1));
                store(samples+2*(i+quarter),multiply(half_sub(ac,bd),w2));
                store(samples+2*(i+2*quarter),multiply(cross(ac_diff,bd_diff,!INVERSE,1),w1));
                store(samples+2*(i+3*quarter),multiply(cross(ac_diff,bd_diff,INVERSE,1),w3));
            }
        }
        modifier*=4;
    }
    for (unsigned i=0;i<length;i+=4) {
        complex_q15 a=load(samples+2*i),b=load(samples+2*i+2),c=load(samples+2*i+4),d=load(samples+2*i+6);
        complex_q15 ac=add(a,c),bd=add(b,d),ac_diff=sub(a,c),bd_diff=sub(b,d);
        store(samples+2*i,half_add(ac,bd));store(samples+2*i+2,half_sub(ac,bd));
        store(samples+2*i+4,cross(ac_diff,bd_diff,!INVERSE,1));store(samples+2*i+6,cross(ac_diff,bd_diff,INVERSE,1));
    }
}
