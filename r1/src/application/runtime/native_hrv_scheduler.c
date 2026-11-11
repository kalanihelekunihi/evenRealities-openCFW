#include <stdint.h>
#include <stddef.h>
#include "native_hrv_timing.h"
extern uint32_t r1_cfg_byte_get_73798(void),r1_health_mode_get(void),r1_structured_log_local_timestamp(void);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_algo_hrv_timing_timeout(uint32_t),r1_hrv_stream_release(void);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static void message(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003,sdk);
}
/* This non-inlined C boolean helper adds eight bytes to the production
 * caller frame (24), preserving the stock NV record offset of 104 bytes.
 * The getter consumes unwritten record bytes; revalidate under compiler changes. */
__attribute__((noinline)) static uint32_t scheduler_health_enabled(void)
{
    return r1_cfg_byte_get_73798()!=0;
}
__attribute__((section(".text.r1_hrv_timing_start_plan")))
void r1_hrv_timing_start_plan(uint32_t hourly)
{
    if (r1_hrv_timing_state.flag1|r1_hrv_timing_state.flag2) return;
    if (r1_hrv_timing_state.mode!=1) return;
    if (!scheduler_health_enabled()) {
        message("[RING]health disabled, skip hrv timing mode","health disabled, skip hrv timing mode");
        return;
    }
    if (!r1_health_mode_get()) return;
    if (r1_hrv_timing_state.timer) return;
    if (r1_hrv_timing_state.stream) return;
    uint32_t seconds=120;
    if (!hourly) {
        uint32_t remaining=3600-r1_structured_log_local_timestamp()%3600u;
        if (remaining<=150) return;
        remaining-=30;
        if (remaining<120) seconds=remaining;
        if (!seconds) return;
    }
    uint32_t timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_algo_hrv_timing_timeout,seconds*1000,0);
    r1_hrv_timing_state.timer=timer;
    if (!timer) {
        message("[RING]algo hrv timing timeout handler create failed","algo hrv timing timeout handler create failed");
        return;
    }
    __aeabi_memclr(r1_hrv_session_buffer,208);
    uint32_t stream=r1_sensor_stream_register_by_name("hrv","algo",(uintptr_t)r1_hrv_producer,1,1);
    r1_hrv_timing_state.stream=stream;
    if (!stream) {
        message("[RING]algo hrv timing register failed","algo hrv timing register failed");
        r1_hrv_stream_release();
        return;
    }
    const char *label=hourly?"hourly":"catchup";
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c800000,"[RING]algo hrv timing start, %s, timeout:%d sec",
            "[RING]algo hrv timing start, %s, timeout:%d sec",label,seconds);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003,"algo hrv timing start, %s, timeout:%d sec",(uint32_t)(uintptr_t)label,seconds);
}
