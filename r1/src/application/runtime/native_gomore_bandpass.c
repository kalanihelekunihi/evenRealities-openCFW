#include <stdint.h>
extern float r1_native_cosf(float),r1_native_sinf(float),r1_native_tanf(float);
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
static __attribute__((noinline,noclone)) float sub(float a,float b){return a-b;}
static __attribute__((noinline,noclone)) float mul(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) float madd(float acc,float a,float b){return acc+a*b;}
static __attribute__((noinline,noclone)) float msub(float acc,float a,float b){return acc-a*b;}
static float sample(uint32_t p){return *(volatile float *)(uintptr_t)p;}
static void put(uint32_t p,float value){*(volatile float *)(uintptr_t)p=value;}
static float width(uint32_t p){float high=sample(p+4u),low=sample(p);return sub(high,low);}
void r1_gomore_coefficients_bandpass_native(uint32_t state,uint32_t order,uint32_t parameters)
{
    volatile uint32_t frame_reservation[4];frame_reservation[0]=0;(void)frame_reservation;
    volatile float imag[4],real[4],imag_first[2],real_first[2],imag_second[2],real_second[2];
    *(volatile uint32_t *)(uintptr_t)(state+4u)=0;
    float low=sample(parameters),high=sample(parameters+4u);
    float center_cosine=r1_native_cosf(mul(mul(add(low,high),0x1.921fb6p+1f),0.5f));
    float width_cosine=r1_native_cosf(mul(mul(width(parameters),0x1.921fb6p+1f),0.5f));
    float width_sine=r1_native_sinf(mul(mul(width(parameters),0x1.921fb6p+1f),0.5f));
    float full_cosine=r1_native_cosf(mul(width(parameters),0x1.921fb6p+1f));
    float full_sine=r1_native_sinf(mul(width(parameters),0x1.921fb6p+1f));
    float tangent=r1_native_tanf(mul(mul(width(parameters),0x1.921fb6p+1f),0.5f));
    float reciprocal=divide(1.0f,tangent),gain=1.0f,accumulator=0.0f;
    for(uint32_t i=0;(int32_t)i<(int32_t)order;i++) {
        float angle=divide(mul((float)(int32_t)(i*2u+1u),0x1.921fb6p+1f),(float)(int32_t)(order*2u));
        float pole_cosine=r1_native_cosf(angle),pole_sine=r1_native_sinf(angle);
        float term=add(pole_sine,reciprocal),previous=gain;
        gain=madd(mul(term,previous),accumulator,pole_cosine);
        float next=mul(add(previous,accumulator),sub(add(reciprocal,pole_sine),pole_cosine));
        next=msub(next,previous,term);accumulator=madd(next,accumulator,pole_cosine);
        float denominator=madd(1.0f,full_sine,pole_sine);
        real_second[i]=divide(full_cosine,denominator);
        imag_second[i]=divide(mul(full_sine,pole_cosine),denominator);
        float width_term=madd(width_cosine,width_sine,pole_sine);
        float scale=mul(center_cosine,-2.0f);
        real_first[i]=divide(mul(scale,width_term),denominator);
        imag_first[i]=divide(mul(mul(scale,width_sine),pole_cosine),denominator);
    }
    if((int32_t)order>0) {
        real[0]=real_first[0];imag[0]=imag_first[0];
        real[1]=real_second[0];imag[1]=imag_second[0];
    }
    for(uint32_t i=1;(int32_t)i<(int32_t)order;i++) {
        uint32_t p=i*2u;
        real[p+1u]=0.0f;real[p]=0.0f;imag[p+1u]=0.0f;imag[p]=0.0f;
        float af=imag_first[i],bs=real_second[i],bf=real_first[i],as=imag_second[i];
        for(uint32_t j=i;(int32_t)j>0;j--) {
            uint32_t k=j*2u;
            float a=real[k-1u],b=real[k],d=imag[k];
            float value=madd(mul(a,bs),b,bf),c=imag[k-1u];
            value=msub(value,c,as);value=msub(value,d,af);real[k+1u]=add(value,real[k+1u]);
            a=real[k-1u];value=madd(mul(a,as),d,bf);float old_imaginary=imag[k+1u];
            value=madd(value,c,bs);b=real[k];value=madd(value,b,af);imag[k+1u]=add(value,old_imaginary);
            float e=real[k-2u],f=imag[k-2u];value=madd(mul(e,bs),a,bf);c=imag[k-1u];
            value=msub(value,f,as);value=msub(value,c,af);real[k]=add(value,b);
            e=real[k-2u];a=real[k-1u];value=madd(mul(e,as),a,af);value=madd(value,f,bs);value=madd(value,c,bf);imag[k]=add(value,imag[k]);
        }
        float a=real[0],b=imag[0];
        float value=msub(madd(bs,a,bf),b,af);real[1]=add(value,real[1]);
        value=madd(madd(as,a,af),b,bf);imag[1]=add(value,imag[1]);
        real[0]=add(a,bf);imag[0]=add(b,af);
    }
    put(state+8u,1.0f);
    for(uint32_t i=1;(int32_t)i<=(int32_t)(order*2u);i++) put(state+8u+i*4u,real[i-1u]);
    float first=divide(1.0f,gain);put(state+28u,first);put(state+32u,0.0f);put(state+36u,first);
    for(uint32_t i=1;(int32_t)i<(int32_t)order;i++) {
        put(state+28u+(i*2u+1u)*4u,0.0f);put(state+28u+(i*2u+2u)*4u,0.0f);
        for(uint32_t j=i+1u;(int32_t)j>0;j--) {
            float a=sample(state+28u+j*8u),b=sample(state+28u+(j*2u-2u)*4u);put(state+28u+j*8u,add(a,b));
        }
    }
    for(uint32_t i=2;(int32_t)i<(int32_t)(order*2u+1u);i+=4u) put(state+28u+i*4u,-sample(state+28u+i*4u));
}
