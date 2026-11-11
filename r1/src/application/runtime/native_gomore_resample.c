#include <stdint.h>
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_gomore_acc_kernel_native(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_ppg_kernel_native(uint32_t,uint32_t,uint32_t,volatile float *);
extern void r1_gomore_log_native(uint32_t,uint32_t,const char *,...);
/* Preserve VADD operand order: two quiet NaNs select the first operand. */
static __attribute__((noinline,noclone)) float ordered_add(float previous,float sample)
{ return previous+sample; }
uint32_t r1_gomore_acc_resample_native(uint32_t context,volatile uint32_t *sources,uint32_t count,volatile uint32_t *outputs)
{
    __aeabi_memclr((void *)(uintptr_t)outputs[0],100);
    __aeabi_memclr((void *)(uintptr_t)outputs[1],100);
    __aeabi_memclr((void *)(uintptr_t)outputs[2],100);
    ((volatile uint8_t *)outputs)[12]=0;
    uint32_t status=0;
    if (!count) { status=32;((volatile uint8_t *)outputs)[12]=1; }
    else for (uint32_t i=0;i<3;i++) {
        uint32_t output=outputs[i];
        uint32_t source=sources[i];
        (void)r1_gomore_acc_kernel_native(context+80u+i*80u,source,count,output);
    }
    (void)r1_gomore_log_native(2,2,"[SnP][ACC]status:%u\r\n",status);
    return status;
}
uint32_t r1_gomore_ppg_resample_native(uint32_t context,volatile uint32_t *sources,uint32_t channels,uint32_t count,volatile uint32_t *output)
{
    /* 112 bytes plus eight saved registers: stock scratch is entry SP - 140. */
    volatile struct { float reciprocal; float scratch[25]; uint32_t saved_padding[2]; } frame;
    _Static_assert(sizeof(frame)==112,"native PPG frame reservation");
    __aeabi_memclr((void *)frame.scratch,100);
    __aeabi_memclr((void *)(uintptr_t)*output,100);
    ((volatile uint8_t *)output)[4]=0;
    uint32_t status=0;
    if (!count || !channels) { status=64;((volatile uint8_t *)output)[4]=1; }
    else {
        frame.reciprocal=1.0f/(float)(int32_t)channels;
        int32_t limit=(int32_t)channels>1?1:(int32_t)channels;
        for (int32_t i=0;i<limit;i++) {
            (void)r1_gomore_ppg_kernel_native(context+(uint32_t)i*80u,sources[i],count,frame.scratch);
            for (uint32_t j=0;j<25;j++) {
                volatile float *destination=(volatile float *)(uintptr_t)(*output+j*4u);
                float sample=frame.scratch[j];
                float previous=*destination;
                *destination=ordered_add(previous,sample);
            }
        }
        for (uint32_t j=0;j<25;j++) {
            volatile float *destination=(volatile float *)(uintptr_t)(*output+j*4u);
            *destination=*destination*frame.reciprocal;
        }
    }
    (void)r1_gomore_log_native(2,2,"[SnP][Ppg]status:%u\r\n",status);
    return status;
}
