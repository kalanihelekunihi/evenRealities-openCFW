/* SPDX-License-Identifier: MIT */
/* Scalar recovery of the packed Q15 first stage and final scaling.
 * Signed shifts follow the C-SKY compiler's arithmetic-shift convention.
 * Product sums explicitly wrap at 32 bits before the final shift. */
#include <stdint.h>
extern void backup_radix4(int16_t *,unsigned,const int16_t *,unsigned);
extern void backup_radix4_inverse(int16_t *,unsigned,const int16_t *,unsigned);
static __attribute__((noinline)) void radix4_by2(int16_t *samples,unsigned length,const int16_t *coefficients,unsigned inverse)
{
    unsigned half=length>>1;
    for (unsigned i=0;i<half;i++) {
        int32_t c=coefficients[2*i],s=coefficients[2*i+1];
        int32_t ar=samples[2*i]>>1,ai=samples[2*i+1]>>1;
        int32_t br=samples[2*(i+half)]>>1,bi=samples[2*(i+half)+1]>>1;
        int32_t dr=ar-br,di=ai-bi;
        samples[2*i]=(int16_t)((ar+br)>>1);
        samples[2*i+1]=(int16_t)((ai+bi)>>1);
        uint32_t real=(uint32_t)(dr*c);
        uint32_t imag=(uint32_t)(di*c);
if (inverse) {
        real-=(uint32_t)(di*s);
        imag+=(uint32_t)(dr*s);
} else {
        real+=(uint32_t)(di*s);
        imag-=(uint32_t)(dr*s);
}
        samples[2*(i+half)]=(int16_t)((int32_t)real>>16);
        samples[2*(i+half)+1]=(int16_t)((int32_t)imag>>16);
    }
    if (inverse) {
        backup_radix4_inverse(samples,half,coefficients,2);
        backup_radix4_inverse(samples+length,half,coefficients,2);
    } else {
        backup_radix4(samples,half,coefficients,2);
        backup_radix4(samples+length,half,coefficients,2);
    }
    for (unsigned i=0;i<half*4;i++)
        samples[i]=(int16_t)((uint16_t)samples[i]*2u);
}
void open_cfw_gx8002_backup_radix4_by2(int16_t *p,unsigned n,const int16_t *c) { radix4_by2(p,n,c,0); }
void open_cfw_gx8002_backup_radix4_by2_inverse(int16_t *p,unsigned n,const int16_t *c) { radix4_by2(p,n,c,1); }
