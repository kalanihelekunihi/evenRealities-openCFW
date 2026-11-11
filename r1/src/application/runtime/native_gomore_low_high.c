#include <stdint.h>
extern float r1_native_cosf(float),r1_native_sinf(float),r1_native_powf(float,float);
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
static __attribute__((noinline,noclone)) float mul(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) float madd(float acc,float a,float b){return acc+a*b;}
static __attribute__((noinline,noclone)) float msub(float acc,float a,float b){return acc-a*b;}
static float read_float(uint32_t a){return *(volatile float *)(uintptr_t)a;}
static void put_float(uint32_t a,float v){*(volatile float *)(uintptr_t)a=v;}
void r1_gomore_coefficients_low_high_native(uint32_t state,uint32_t mode,uint32_t order,float cutoff)
{
    volatile float polynomial_imaginary[4],polynomial_real[4],root_imaginary[4],root_real[4];
    *(volatile uint32_t *)(uintptr_t)(state+4u)=0;
    float angle=mul(cutoff,0x1.921fb6p+1f);
    float cosine=r1_native_cosf(angle),sine=r1_native_sinf(angle),gain=1.0f;
    for(uint32_t i=0;(int32_t)i<(int32_t)order;i++) {
        float pole_angle=divide(mul((float)(int32_t)(i*2u+1u),0x1.921fb6p+1f),(float)(int32_t)(order*2u));
        float pole_cosine=r1_native_cosf(pole_angle),pole_sine=r1_native_sinf(pole_angle);
        if((int32_t)i<(int32_t)order/2) gain=mul(madd(1.0f,sine,pole_sine),gain);
        float denominator=madd(1.0f,sine,pole_sine);
        root_real[i]=divide(-cosine,denominator);
        root_imaginary[i]=divide(mul(-sine,pole_cosine),denominator);
    }
    if((int32_t)order>0) {
        polynomial_real[0]=root_real[0];polynomial_imaginary[0]=root_imaginary[0];
    }
    for(uint32_t i=1;(int32_t)i<(int32_t)order;i++) {
        polynomial_real[i]=0.0f;polynomial_imaginary[i]=0.0f;
        float real=root_real[i],imaginary=root_imaginary[i];
        for(uint32_t j=i;(int32_t)j>0;j--) {
            float a=polynomial_real[j-1],b=polynomial_imaginary[j-1];
            float term=msub(mul(a,real),b,imaginary);
            polynomial_real[j]=add(term,polynomial_real[j]);
            a=polynomial_real[j-1];
            term=madd(mul(a,imaginary),b,real);
            polynomial_imaginary[j]=add(term,polynomial_imaginary[j]);
        }
        polynomial_real[0]=add(polynomial_real[0],real);
        polynomial_imaginary[0]=add(polynomial_imaginary[0],imaginary);
    }
    put_float(state+8u,1.0f);
    for(uint32_t i=1;(int32_t)i<=(int32_t)order;i++) put_float(state+8u+i*4u,polynomial_real[i-1]);
    float half_angle=mul(angle,0.5f);
    float half_cosine=r1_native_cosf(half_angle),half_sine=r1_native_sinf(half_angle);
    if(order&1u) gain=mul(add(half_cosine,half_sine),gain);
    float powered=r1_native_powf(mode?half_cosine:half_sine,(float)(int32_t)order);
    put_float(state+28u,divide(powered,gain));
    put_float(state+32u,read_float(state+28u));
    for(uint32_t i=1;(int32_t)i<(int32_t)order;i++) {
        put_float(state+28u+(i+1u)*4u,0.0f);
        for(uint32_t j=i+1u;(int32_t)j>0;j--) {
            float a=read_float(state+28u+j*4u),b=read_float(state+28u+(j-1u)*4u);
            put_float(state+28u+j*4u,add(a,b));
        }
    }
    if(mode) for(uint32_t i=1;(int32_t)i<(int32_t)(order+1u);i+=2u) put_float(state+28u+i*4u,-read_float(state+28u+i*4u));
}
