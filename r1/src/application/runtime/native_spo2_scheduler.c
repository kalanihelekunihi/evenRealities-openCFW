#include <stdint.h>
#include "native_spo2_timing.h"
extern uint32_t r1_cfg_byte_get_73798(void),r1_health_mode_get(void),r1_structured_log_local_timestamp(void);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static void message(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003,sdk);
}
/* The volatile C local gives this helper a 16-byte production frame.
 * Together with the caller24, it preserves the native raw NV record offset112.
 * Failed/partial reads consume unwritten bytes; revalidate compiler changes. */
__attribute__((noinline)) static uint32_t scheduler_health_enabled(void)
{
    volatile uint32_t flag=r1_cfg_byte_get_73798();
    return flag!=0;
}
__attribute__((section(".text.r1_spo2_timing_start_plan")))
void r1_spo2_timing_start_plan(uint32_t hourly)
{
    if (r1_spo2_timing_state.flag1|r1_spo2_timing_state.flag2) return;
    if (r1_spo2_timing_state.mode!=1) return;
    if (!scheduler_health_enabled()) {
        message("[RING]health disabled, skip spo2 timing mode","health disabled, skip spo2 timing mode");
        return;
    }
    if (!r1_health_mode_get()) return;
    if (r1_spo2_streams[1]) return;
    uint32_t seconds=120;
    if (!hourly) {
        uint32_t remaining=3600-r1_structured_log_local_timestamp()%3600u;
        if (remaining<=150) return;
        remaining-=30;
        if (remaining<120) seconds=remaining;
        if (!seconds) return;
    }
    uint32_t stream=r1_sensor_stream_register_by_name("spo2","timing",(uintptr_t)r1_spo2_timing_sample,1,1);
    r1_spo2_streams[1]=stream;
    if (!stream) {
        message("[RING]algo spo2 timing register failed","algo spo2 timing register failed");
        return;
    }
    uint32_t timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_spo2_timing_timeout,seconds*1000,0);
    r1_spo2_timing_state.timer=timer;
    if (!timer) {
        message("[RING]algo spo2 timing timeout handler create failed","algo spo2 timing timeout handler create failed");
        r1_sensor_stream_unregister_by_name("spo2",r1_spo2_streams[1]);
        r1_spo2_streams[1]=0;
        return;
    }
    const char *label=hourly?"hourly":"catchup";
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c800000,"[RING]algo spo2 timing start, %s, timeout:%d sec",
            "[RING]algo spo2 timing start, %s, timeout:%d sec",label,seconds);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003,"algo spo2 timing start, %s, timeout:%d sec",(uint32_t)(uintptr_t)label,seconds);
}
