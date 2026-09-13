/* SPDX-License-Identifier: MIT */
/* Scalar recovery of the packed Q15 first stage and final scaling.
 * Signed shifts follow the C-SKY compiler's arithmetic-shift convention.
 * Product sums explicitly wrap at 32 bits before the final shift. */
#include <stdint.h>
extern void backup_radix4(int16_t *,unsigned,const int16_t *,unsigned);
extern void backup_radix4_inverse(int16_t *,unsigned,const int16_t *,unsigned);
#ifndef INVERSE
#define INVERSE 0
#endif
#if INVERSE
#define ENTRY open_cfw_gx8002_backup_radix4_by2_inverse
#define RADIX backup_radix4_inverse
#else
#define ENTRY open_cfw_gx8002_backup_radix4_by2
#define RADIX backup_radix4
#endif
void ENTRY(int16_t *samples,unsigned length,const int16_t *coefficients)
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
#if INVERSE
        real-=(uint32_t)(di*s);
        imag+=(uint32_t)(dr*s);
#else
        real+=(uint32_t)(di*s);
        imag-=(uint32_t)(dr*s);
#endif
        samples[2*(i+half)]=(int16_t)((int32_t)real>>16);
        samples[2*(i+half)+1]=(int16_t)((int32_t)imag>>16);
    }
    RADIX(samples,half,coefficients,2);
    RADIX(samples+length,half,coefficients,2);
    for (unsigned i=0;i<half*4;i++)
        samples[i]=(int16_t)((uint16_t)samples[i]*2u);
}
