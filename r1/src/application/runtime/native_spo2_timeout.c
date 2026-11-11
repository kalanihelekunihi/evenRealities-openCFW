#include <stdint.h>
#include "native_spo2_timing.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);

__attribute__((section(".text.r1_spo2_timing_timeout")))
void r1_spo2_timing_timeout(uint32_t timer)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,
            "[RING]algo spo2 timing timeout","[RING]algo spo2 timing timeout");
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003,"algo spo2 timing timeout");
    uint32_t handle=r1_spo2_streams[1];
    if (handle) {
        r1_sensor_stream_unregister_by_name("spo2",handle);
        r1_spo2_streams[1]=0;
    }
    (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
    r1_spo2_timing_state.timer=0;
    r1_spo2_timing_state.flag2=1;
}
