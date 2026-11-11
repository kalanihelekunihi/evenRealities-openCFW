#include <stdint.h>
#include "native_hrv_timing.h"
extern void r1_hr_session_teardown(void);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);

__attribute__((section(".text.r1_algo_hrv_timing_timeout")))
void r1_algo_hrv_timing_timeout(uint32_t timer)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,
            "[RING]algo hrv timing timeout","[RING]algo hrv timing timeout");
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003,"algo hrv timing timeout");
    r1_hr_session_teardown();
    (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
    r1_hrv_timing_state.timer=0;
    r1_hrv_timing_state.flag2=1;
}
