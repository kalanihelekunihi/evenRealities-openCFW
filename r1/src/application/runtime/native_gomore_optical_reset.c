#include <stdint.h>
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
extern void r1_gomore_coefficients_low_high_native(uint32_t,uint32_t,uint32_t,float);
extern void r1_gomore_coefficients_bandpass_native(uint32_t,uint32_t,uint32_t);
uint32_t r1_gomore_filter_configure_native(uint32_t state,uint32_t mode,uint32_t count,uint32_t parameters)
{
    if((int32_t)mode<2) {
        float cutoff=*(volatile float *)(uintptr_t)parameters;
        r1_gomore_coefficients_low_high_native(state,mode,count,cutoff);
        *(volatile uint32_t *)(uintptr_t)state=count;
    } else if(mode==2) {
        r1_gomore_coefficients_bandpass_native(state,count,parameters);
        *(volatile uint32_t *)(uintptr_t)state=count<<1;
    }
    for(uint32_t i=0;i<4;i++) {
        *(volatile float *)(uintptr_t)(state+64u+i*4u)=0.0f;
        *(volatile float *)(uintptr_t)(state+48u+i*4u)=0.0f;
    }
    return state;
}
uint32_t r1_gomore_optical_reset_native(uint32_t state)
{
    volatile uint32_t parameters[2];
    __aeabi_memclr((void *)(uintptr_t)state,1736);
    *(volatile uint8_t *)(uintptr_t)(state+80u)=0;
    *(volatile float *)(uintptr_t)(state+1728u)=-1.0f;
    *(volatile float *)(uintptr_t)(state+1732u)=-1.0f;
    *(volatile uint32_t *)(uintptr_t)(state+84u)=0;
    *(volatile uint8_t *)(uintptr_t)(state+81u)=0;
    for(uint32_t i=0;i<250;i++) *(volatile float *)(uintptr_t)(state+728u+i*4u)=0.0f;
    parameters[0]=0x3d23d70a;parameters[1]=0x3ea3d70a;
    (void)r1_gomore_filter_configure_native(state,2,2,(uint32_t)(uintptr_t)parameters);
    return 0;
}
