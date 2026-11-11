#include <stdint.h>
#include <stddef.h>
#include "native_hrv_timing.h"
extern float r1_hrv_rmssd(const volatile void *,uint32_t);
extern uint32_t r1_health_mode_is_2(void),r1_time_backend_timestamp(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern void r1_hr_session_teardown(void),__aeabi_memclr(void *,size_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
typedef uint16_t r1_hrv_half __attribute__((may_alias));
static uint32_t load_half(uint32_t address)
{ return *(const volatile r1_hrv_half *)(uintptr_t)address; }
static void store_half(uint32_t address,uint32_t value)
{ *(volatile r1_hrv_half *)(uintptr_t)address=(uint16_t)value; }
static int positive(float value)
{
    /* Strict GCC floating-point flags preserve stock signaling NaN behavior. */
    return value>0.0f;
}
static uint32_t truncate_unsigned(float value)
{
    union { float value; uint32_t bits; } input={.value=value};
    /* Only positive, non-NaN values reach this conversion. */
    if (input.bits>=0x4f800000u) {
        /* Stock saturates and raises invalid; avoid an out-of-range C cast. */
        volatile float zero=0.0f;
        volatile float invalid=zero/zero;
        (void)invalid;
        return UINT32_MAX;
    }
    return (uint32_t)value;
}
__attribute__((section(".text.r1_hrv_producer")))
void r1_hrv_producer(uint32_t context,const volatile void *payload,uint32_t length)
{
    (void)context;(void)length;
    uint32_t buffer=(uint32_t)(uintptr_t)r1_hrv_session_buffer;
    uint32_t data=(uint32_t)(uintptr_t)payload;
    uint32_t attempts=(uint16_t)(load_half(buffer+206)+1u);
    store_half(buffer+206,attempts);
    if (attempts<10) return;
    for (uint8_t i=0;*(const volatile uint8_t *)(uintptr_t)(data+9u)>i && i<4;i++) {
        uint32_t sample=data+(uint32_t)i*2u;
        if (!load_half(sample)) continue;
        uint32_t used=load_half(buffer+202),head=load_half(buffer+200),index;
        if (used>=100) {
            if (load_half(buffer+head*2u))
                store_half(buffer+204,load_half(buffer+204)-1u);
            store_half(buffer+200,(head+1u)%100u);
            index=head;
        } else {
            index=(head+used)%100u;
            store_half(buffer+202,used+1u);
        }
        store_half(buffer+index*2u,load_half(sample));
        store_half(buffer+204,load_half(buffer+204)+1u);
    }
    if (load_half(buffer+206)<60 || load_half(buffer+204)<70) return;
    float value=r1_hrv_rmssd(r1_hrv_session_buffer,load_half(buffer+202));
    uint32_t had_timer=r1_hrv_timing_state.timer!=0;
    if (positive(value) && r1_health_mode_is_2()) {
        struct {uint16_t value,padding;uint32_t timestamp;} record={0,0,0};
        record.timestamp=r1_time_backend_timestamp();
        record.value=(uint16_t)truncate_unsigned(value);
        (void)r1_event_publish(7,&record,8);
        r1_hr_session_teardown();
        if (had_timer) {
            r1_hrv_stream_release();
            r1_hrv_timing_state.flag1=1;
        }
        return;
    }
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,
            "[RING]RMSSD calculation failed","[RING]RMSSD calculation failed");
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003,"RMSSD calculation failed");
    if (had_timer) __aeabi_memclr(r1_hrv_session_buffer,208);
    else r1_hr_session_teardown();
}
