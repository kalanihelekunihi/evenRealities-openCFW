#include <stdint.h>
#include <stddef.h>
#include "native_float_bits.h"
extern void *pvPortMalloc(size_t);
extern uint32_t vPortFree(void *);
extern void *memset(void *,int,size_t);
extern uint32_t r1_activity_mode_byte_get(void),r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern float r1_native_sqrtf(float);
static void allocation_failed(uint32_t count,const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,ring,ring,count);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,sdk,count);
}
static double promote(float value)
{
    union {float f;uint32_t u;} input={.f=value};
    union {uint64_t u;double d;} output={.u=r1_binary32_to_binary64_bits(input.u)};
    return output.d;
}
static uint32_t log_unsigned(float value)
{
    union {float value;uint32_t bits;} input={.value=value};
    uint32_t magnitude=input.bits&0x7fffffffu;
    uint32_t negative=input.bits>>31;
    if (magnitude>0x7f800000u ||
        (negative && magnitude>=0x3f800000u) ||
        (!negative && magnitude>=0x4f800000u)) {
        /* Native invalid conversions saturate without an out-of-range C cast. */
        volatile float zero=0.0f;
        volatile float invalid=zero/zero;
        (void)invalid;
        return !negative && magnitude<=0x7f800000u ? UINT32_MAX : 0u;
    }
    return (uint32_t)value;
}
__attribute__((section(".text.r1_hrv_rmssd")))
float r1_hrv_rmssd(const volatile void *samples,uint32_t count)
{
    if (!samples || count<2) return -1.0f;
    const volatile uint16_t *input=samples;
    volatile uint8_t *valid=pvPortMalloc(count);
    if (!valid) {
        allocation_failed(count,"[RING]RMSSD fail: malloc valid_flags failed, n=%d",
            "RMSSD fail: malloc valid_flags failed, n=%d");
        return -1.0f;
    }
    (void)memset((void *)(uintptr_t)valid,1,count);
    uint32_t upper=r1_activity_mode_byte_get()==1?1500:1100;
    for (uint16_t i=1;i<count;i++) {
        uint32_t current=input[i];
        int32_t delta=(int32_t)current-(int32_t)input[(uint32_t)i-1u];
        if ((uint32_t)delta+150u>300u || current>upper) {
            valid[i]=0;
            valid[(uint32_t)i-1u]=0;
        }
    }
    uint32_t bytes=count*2u-2u;
    volatile uint16_t *differences=pvPortMalloc(bytes);
    if (!differences) {
        (void)vPortFree((void *)(uintptr_t)valid);
        allocation_failed(count,"[RING]RMSSD fail: malloc filtered_diff failed, n=%d",
            "RMSSD fail: malloc filtered_diff failed, n=%d");
        return -1.0f;
    }
    (void)memset((void *)(uintptr_t)differences,0,bytes);
    uint16_t accepted=0;
    for (uint16_t i=1;i<count;i++) {
        if (valid[(uint32_t)i-1u] && valid[i]) {
            int32_t delta=(int32_t)input[i]-(int32_t)input[(uint32_t)i-1u];
            differences[accepted]=(uint16_t)(delta<0?-delta:delta);
            accepted++;
        }
    }
    float sum=-1.0f,mean=-1.0f,result=-1.0f;
    if (accepted) {
        sum=0.0f;
        for (uint16_t i=0;i<accepted;i++) {
            uint32_t difference=differences[i];
            union {uint32_t u;int32_t i;} square={.u=difference*difference};
            sum=(float)square.i+sum;
        }
        mean=sum/(float)accepted;
        result=r1_native_sqrtf(mean);
    }
    (void)vPortFree((void *)(uintptr_t)valid);
    (void)vPortFree((void *)(uintptr_t)differences);
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        double sum64=promote(sum),mean64=promote(mean),result64=promote(result);
        (void)r1_structured_log_format(0x0d000000,
            "[RING]RMSSD result: rmssd=%1.2f, mean_sq=%1.2f, sum_sq=%1.2f, diff_count=%d",
            "[RING]RMSSD result: rmssd=%1.2f, mean_sq=%1.2f, sum_sq=%1.2f, diff_count=%d",result64,mean64,sum64,accepted);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t sum32=log_unsigned(sum),mean32=log_unsigned(mean),result32=log_unsigned(result);
        nrf_log_frontend_std_4(0x001c0003,"RMSSD result: rmssd=%1.2f, mean_sq=%1.2f, sum_sq=%1.2f, diff_count=%d",
            result32,mean32,sum32,accepted);
    }
    return result;
}
