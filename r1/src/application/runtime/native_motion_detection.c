#include <stdint.h>
#include "native_float_to_signed.h"
#include <stddef.h>
#include "../board/native_battery_memory.h"
#pragma STDC FP_CONTRACT OFF

volatile uint8_t r1_motion_detection_state[48] __attribute__((section(".bss.r1.motion.detection.state"),aligned(4)));
volatile uint16_t r1_motion_detection_log_count __attribute__((section(".r1.motion.detection.log_count"),aligned(2)))=0;
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern float r1_native_sqrtf(float);
extern void r1_native_motion_detection_classify(float);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
static float number(uint32_t bits) {union {uint32_t u;float f;} x={.u=bits};return x.f;}
static uint32_t bits(float value) {union {float f;uint32_t u;} x={.f=value};return x.u;}
static float load_float(const volatile uint8_t *p) {return number(read32(p));}
static void store_float(volatile uint8_t *p,float value) {write32(p,bits(value));}
/* Keep a separate call so the recorded Clang profile retains left/right
 * operand order, including native NaN payload precedence. */
static __attribute__((noinline)) float ordered_add(float left,float right)
{return left+right;}
static uint32_t log_integer(float value)
{
    return r1_native_float_to_signed32(value);
}
void r1_motion_detection_ring_push(float value)
{
    volatile uint8_t *state=r1_motion_detection_state;
    uint32_t count=read16(state+34),index=state[32];
    volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)
        ((uint32_t)(uintptr_t)state+index*4u);
    if (count>=8) {
        float sum=load_float(state+44),old=load_float(entry);
        store_float(state+44,sum-old);
    }
    store_float(entry,value);
    float sum=load_float(state+44);
    store_float(state+44,ordered_add(sum,value));
    state[32]=(uint8_t)((state[32]+1u)&7u);
    count=read16(state+34);
    if (count<8) write16(state+34,count+1u);
}
void r1_motion_detection_sample(void *node __attribute__((unused)),uint32_t payload,
        uint32_t length __attribute__((unused)))
{
    const volatile uint8_t *input=(const volatile uint8_t *)(uintptr_t)payload;
    uint32_t count=input[180]; /* Stock faults on null before its null branch. */
    if (!payload) return;
    if (count>25) count=25;
    else if (count<20) return;
    uint32_t stride=count/5u;
    if (!stride) stride=1;
    float sum=0.0f;uint32_t accepted=0;
    for (uint32_t i=0;i<5 && i*stride<count;i++) {
        const volatile uint8_t *sample=input+(uint8_t)(i*stride)*6u;
        int32_t x=(int16_t)read16(sample),y=(int16_t)read16(sample+2),z=(int16_t)read16(sample+4);
        float xf=(float)x*number(0x3a800000),yf=(float)y*number(0x3a800000),zf=(float)z*number(0x3a800000);
        float square=xf*xf;square=square+yf*yf;square=square+zf*zf;
        float delta=__builtin_fabsf(r1_native_sqrtf(square)-1.0f);
        if ((int32_t)bits(delta)<INT32_C(0x40a00000)) {sum=sum+delta;accepted++;}
    }
    if (!accepted) return;
    volatile uint8_t *state=r1_motion_detection_state;
    float average=sum/(float)accepted;
    float next=number(0x3f333333)*average;
    float previous=load_float(state+40);
    next=next+number(0x3e99999a)*previous;
    store_float(state+40,next);
    r1_motion_detection_ring_push(next);
    r1_native_motion_detection_classify(load_float(state+40));
    uint32_t ticks=(uint16_t)(r1_motion_detection_log_count+1u);
    r1_motion_detection_log_count=(uint16_t)ticks;
    if (ticks>=600) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
            uint32_t flag=state[38],samples=read16(state+36);
            uint32_t raw=log_integer(load_float(state+40)*1000.0f);
            (void)r1_structured_log_format(0x0cc00000,
                "[RING]detect state: raw=%d cnt=%d static=%d",
                "[RING]detect state: raw=%d cnt=%d static=%d",raw,samples,flag);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t flag=state[38];
            uint32_t raw=log_integer(load_float(state+40)*1000.0f);
            uint32_t samples=read16(state+36);
            nrf_log_frontend_std_3(0x001c0003,"detect state: raw=%d cnt=%d static=%d",raw,samples,flag);
        }
        r1_motion_detection_log_count=0;
    }
    state[39]=1;
}
uint32_t r1_native_health_detection_stream_initialize(void)
{
    __aeabi_memclr((void *)r1_motion_detection_state,48);
    return r1_sensor_stream_register_by_name("acc","detect",(uintptr_t)r1_motion_detection_sample,1,0);
}
