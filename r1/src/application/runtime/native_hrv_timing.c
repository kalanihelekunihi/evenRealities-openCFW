#include <stdint.h>
#include <stddef.h>

#include "native_hrv_timing.h"
_Static_assert(sizeof(struct r1_hrv_timing_state)==20,"stock HRV state");
_Static_assert(offsetof(struct r1_hrv_timing_state,timer)==16,"stock timer field");
volatile struct r1_hrv_timing_state r1_hrv_timing_state
    __attribute__((section(".r1.hrv.timing.state"),aligned(4)))={4,0,0,0,0,0,0,0};
uint8_t r1_hrv_session_buffer[208]
    __attribute__((section(".bss.r1.hrv.session.buffer"),aligned(4)))={0};
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern void __aeabi_memclr(void *,size_t);
extern void r1_hrv_timing_start_plan(uint32_t);

__attribute__((section(".text.r1_hr_session_teardown")))
void r1_hr_session_teardown(void)
{
    uint32_t handle=r1_hrv_timing_state.stream;
    if (handle) {
        r1_sensor_stream_unregister_by_name("hrv",handle);
        r1_hrv_timing_state.stream=0;
    }
    __aeabi_memclr(r1_hrv_session_buffer,208);
}

__attribute__((section(".text.r1_hrv_stream_release")))
void r1_hrv_stream_release(void)
{
    uint32_t handle=r1_hrv_timing_state.timer;
    if (handle) {
        (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)handle);
        r1_hrv_timing_state.timer=0;
    }
}

__attribute__((section(".text.r1_native_health_group1_b_callback")))
void r1_native_health_group1_b_callback(void)
{
    if (r1_hrv_timing_state.timer) {
        r1_hr_session_teardown();
        r1_hrv_stream_release();
    }
    r1_hrv_timing_state.flag1=0;
    r1_hrv_timing_state.flag2=0;
    if (r1_hrv_timing_state.mode==1)
        r1_hrv_timing_start_plan(1);
}
