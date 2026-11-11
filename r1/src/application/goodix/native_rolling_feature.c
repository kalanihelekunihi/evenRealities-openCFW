/* Native sensor rolling features: 0x66608,0x9775c,0x36dd4 and
 * the two-range 0x2fee2/0x2f2ac helper. Stock-layout records use live
 * volatile loads; portable goodix_primitives models retain separate APIs.
 */
#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *, const void *, size_t);
static uint32_t word(uintptr_t p, uint32_t o) { return *(const volatile uint32_t *)(p+o); }
static uint16_t half(uintptr_t p, uint32_t o) { return *(const volatile uint16_t *)(p+o); }
static uint8_t byte(uintptr_t p, uint32_t o) { return *(const volatile uint8_t *)(p+o); }
static void put_half(uintptr_t p,uint32_t o,uint16_t v) { *(volatile uint16_t *)(p+o)=v; }
static void put_byte(uintptr_t p,uint32_t o,uint8_t v) { *(volatile uint8_t *)(p+o)=v; }
static float number(uintptr_t p,uint32_t o) { return *(const volatile float *)(p+o); }
static void put_float(uintptr_t p,uint32_t o,float v) { *(volatile float *)(p+o)=v; }
static uint32_t remainder(uint32_t a,uint32_t b) { return b ? a%b : a; }
/* The object profile must retain native accumulator-first NaN selection. */
__attribute__((noinline)) static float add(float accumulator,float sample) { return accumulator+sample; }
void r1_goodix_native_float_window_push(float value,void *record)
{
    uintptr_t p=(uintptr_t)record;
    uint32_t phase=byte(p,9),period=byte(p,8);
    if (remainder(phase,period)==0) {
        uintptr_t values=word(p,0);uint32_t count=half(p,4),capacity=half(p,6);
        float oldest=number(values,0);
        if(count<capacity) {
            put_float(values,count*4u,value);
            put_float(p,12,add(number(p,12),value));
            put_half(p,4,(uint16_t)(half(p,4)+1u));
        } else {
            memmove((void *)values,(const void *)(values+4u),capacity*4u-4u);
            put_float(word(p,0),half(p,6)*4u-4u,value);
            put_float(p,12,add(number(p,12),value)-oldest);
        }
        uint16_t cursor=(uint16_t)(half(p,10)+1u);
        put_half(p,10,cursor);
        if(cursor>=half(p,6))cursor=0;
        put_half(p,10,cursor);
    }
    uint8_t next=(uint8_t)(byte(p,9)+1u);
    put_byte(p,9,next);
    if(next>=byte(p,8))next=0;
    put_byte(p,9,next);
}
float r1_goodix_native_reverse_weighted_sum(const volatile float *weights,uint32_t count,const volatile float *samples,int32_t available)
{
    float sum=0;
    if(available) {
        uint16_t i=0;
        while(i<count) {
            float weight=weights[i];
            uint32_t index=(uint32_t)available-(uint32_t)i-1u;
            if((int32_t)index<=0)index=0;
            float sample=samples[index];
            sum=add(sum,weight*sample);
            i=(uint16_t)(i+1u);
        }
    }
    return sum;
}
static const float smoothing_kernel[25] = {
    0x1.dc727cp-6f, 0x1.025772p-5f, 0x1.15a448p-5f,
    0x1.27e5e0p-5f, 0x1.38e498p-5f, 0x1.486bf0p-5f,
    0x1.564b5ep-5f, 0x1.625716p-5f, 0x1.6c68c0p-5f,
    0x1.74601cp-5f, 0x1.7a237cp-5f, 0x1.7da042p-5f,
    0x1.7ecb1cp-5f, 0x1.7da042p-5f, 0x1.7a237cp-5f,
    0x1.74601cp-5f, 0x1.6c68c0p-5f, 0x1.625716p-5f,
    0x1.564b5ep-5f, 0x1.486bf0p-5f, 0x1.38e498p-5f,
    0x1.27e5e0p-5f, 0x1.15a448p-5f, 0x1.025772p-5f,
    0x1.dc727cp-6f,
};

static const float residual_kernel[25] = {
    -0x1.c91882p-9f, -0x1.0e4ce4p-7f, -0x1.a3657cp-9f,
    -0x1.c84004p-10f, -0x1.8144a2p-6f, -0x1.4b53e2p-5f,
    -0x1.cba8a2p-7f, 0x1.2eb9aep-7f, -0x1.9a8060p-5f,
    -0x1.01e27ep-3f, -0x1.ca4706p-6f, 0x1.0ae292p-2f,
    0x1.d15cacp-2f, 0x1.0ae292p-2f, -0x1.ca4706p-6f,
    -0x1.01e27ep-3f, -0x1.9a8060p-5f, 0x1.2eb9aep-7f,
    -0x1.cba8a2p-7f, -0x1.4b53e2p-5f, -0x1.8144a2p-6f,
    -0x1.c84004p-10f, -0x1.a3657cp-9f, -0x1.0e4ce4p-7f,
    -0x1.c91882p-9f,
};

void r1_goodix_native_rolling_feature(float value,uint32_t sequence,const void *descriptor,void *record)
{
    uintptr_t p=(uintptr_t)record,d=(uintptr_t)descriptor;
    r1_goodix_native_float_window_push(value,(void *)p);
    float smooth=r1_goodix_native_reverse_weighted_sum(smoothing_kernel,25,(const volatile float *)(uintptr_t)word(p,0),half(p,4));
    r1_goodix_native_float_window_push(smooth,(void *)(p+16));
    uint32_t count=half(p,4),index=count>13u?count-13u:0;
    float residual=number(word(p,0),index*4u)-smooth;
    r1_goodix_native_float_window_push(residual,(void *)(p+32));
    float filtered=r1_goodix_native_reverse_weighted_sum(residual_kernel,25,(const volatile float *)(uintptr_t)word(p,32),half(p,36));
    r1_goodix_native_float_window_push(filtered,(void *)(p+48));
    uint32_t period=word(d,80);
    if(remainder(sequence,period)==period-1u) {
        float sum=0;
        for(uint32_t i=0;(int32_t)i<(int32_t)period;i++) {
            uint32_t at=(uint32_t)half(p+16,4)-12u-i-1u;
            if((int32_t)at<=0)at=0;
            /* Stock adds the sample before the accumulator. */
            sum=add(number(word(p,16),at*4u),sum);
        }
        r1_goodix_native_float_window_push(sum/(float)(int32_t)period,(void *)(p+64));
    }
}
void r1_goodix_native_rolling_pair(const volatile float *input,uint32_t sequence,const void *descriptor,void *record)
{
    r1_goodix_native_rolling_feature(input[0],sequence,descriptor,record);
    float sample=input[1];uintptr_t p=(uintptr_t)record;
    uint32_t period=word((uintptr_t)descriptor,84),rem=remainder(sequence,period);
    float sum;
    if(!rem){sum=0;put_float(p,80,sum);}else sum=number(p,80);
    sum=add(sum,sample);put_float(p,80,sum);
    if(rem==period-1u)r1_goodix_native_float_window_push(sum/(float)(int32_t)period,(void *)(p+84));
}
