/* Binary64 helpers for native kernel_rem_pio2 at 0x10010ca4.
 * Bodies follow pinned Android bionic a27d2baa libm/src/s_floor.c and
 * s_scalbn.c (Sun Microsystems fdlibm); the original license notices are
 * preserved in those pinned files. The word macros are expanded here for
 * the little-endian C-SKY target; no host libm substitution is used.
 * Address attribution of these leaf helpers remains open.
 */
#include <stdint.h>

typedef union { double d; uint64_t u; } gx8002_binary64_word;

double gx8002_image_b_floor_double(double x)
{
    gx8002_binary64_word v = {.d=x};
    int32_t i0=(int32_t)(v.u>>32), i1=(int32_t)v.u;
    int32_t j0=((i0>>20)&0x7ff)-0x3ff;
    uint32_t i,j;
    if(j0<20) {
        if(j0<0) {
            if(1.0e300+x>0.0) {
                if(i0>=0) i0=i1=0;
                else if(((i0&0x7fffffff)|i1)!=0) {i0=(int32_t)0xbff00000u;i1=0;}
            }
        } else {
            i=0x000fffffu>>j0;
            if(((i0&(int32_t)i)|i1)==0) return x;
            if(1.0e300+x>0.0) {
                if(i0<0) i0+=(int32_t)(0x00100000u>>j0);
                i0&=~(int32_t)i; i1=0;
            }
        }
    } else if(j0>51) {
        if(j0==0x400) return x+x;
        return x;
    } else {
        i=0xffffffffu>>(j0-20);
        if(((uint32_t)i1&i)==0) return x;
        if(1.0e300+x>0.0) {
            if(i0<0) {
                if(j0==20) i0+=1;
                else {
                    j=(uint32_t)i1+(1u<<(52-j0));
                    if(j<(uint32_t)i1) i0+=1;
                    i1=(int32_t)j;
                }
            }
            i1&=~(int32_t)i;
        }
    }
    v.u=((uint64_t)(uint32_t)i0<<32)|(uint32_t)i1;
    return v.d;
}

double gx8002_image_b_scalbn_double(double x, int n)
{
    const double two54=1.80143985094819840000e+16;
    const double twom54=5.55111512312578270212e-17;
    const double huge=1.0e+300, tiny=1.0e-300;
    gx8002_binary64_word v={.d=x};
    int32_t hx=(int32_t)(v.u>>32), lx=(int32_t)v.u;
    int32_t k=(hx&0x7ff00000)>>20;
    if(k==0) {
        if((lx|(hx&0x7fffffff))==0) return x;
        x*=two54; v.d=x; hx=(int32_t)(v.u>>32);
        k=((hx&0x7ff00000)>>20)-54;
        if(n< -50000) return tiny*x;
    }
    if(k==0x7ff) return x+x;
    k+=n;
    double signed_huge = ((uint32_t)hx&0x80000000u) ? -huge:huge;
    double signed_tiny = ((uint32_t)hx&0x80000000u) ? -tiny:tiny;
    if(k>0x7fe) return huge*signed_huge;
    if(k>0) {
        v.d=x;
        v.u=(v.u&UINT64_C(0x00000000ffffffff))|
            ((uint64_t)(((uint32_t)hx&0x800fffffu)|((uint32_t)k<<20))<<32);
        return v.d;
    }
    if(k<=-54) {
        if(n>50000) return huge*signed_huge;
        return tiny*signed_tiny;
    }
    k+=54; v.d=x;
    v.u=(v.u&UINT64_C(0x00000000ffffffff))|
        ((uint64_t)(((uint32_t)hx&0x800fffffu)|((uint32_t)k<<20))<<32);
    return v.d*twom54;
}
