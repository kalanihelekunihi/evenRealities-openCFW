#include <stdint.h>
#include <stddef.h>
#include "native_hrv_timing.h"
_Static_assert(offsetof(struct r1_hrv_timing_state,hr_timer)==12,"stock HR timer");
volatile uint32_t r1_health_hr_streams[5]
    __attribute__((section(".bss.r1.health.hr.streams"),aligned(4)))={0};
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern void r1_hr_session_teardown(void);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);

__attribute__((section(".text.r1_hr_stream_release")))
void r1_hr_stream_release(void)
{
    uint32_t timer=r1_hrv_timing_state.hr_timer;
    if (timer) {
        (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
        r1_hrv_timing_state.hr_timer=0;
    }
}
__attribute__((section(".text.r1_native_health_group4_b_callback")))
void r1_native_health_group4_b_callback(const volatile void *event)
{
    uint32_t status=*(const volatile uint8_t *)event;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,
            "[RING]algo hr wear status change: %d","[RING]algo hr wear status change: %d",status);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"algo hr wear status change: %d",status);
    if (status==1) return;
    for (uint32_t i=0;i<4;i++) {
        uint32_t handle=r1_health_hr_streams[i];
        if (handle) {
            r1_sensor_stream_unregister_by_name("hr",handle);
            r1_health_hr_streams[i]=0;
        }
    }
    r1_hr_session_teardown();
    r1_hrv_stream_release();
    r1_hr_stream_release();
    (void)r1_gomore_authorization_dispatch_native(5,0);
}
