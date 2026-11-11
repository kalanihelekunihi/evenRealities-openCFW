#include <stdint.h>
#include <stddef.h>
#include "native_spo2_timing.h"
_Static_assert(sizeof(struct r1_spo2_timing_state)==8,"stock SpO2 state");
_Static_assert(offsetof(struct r1_spo2_timing_state,timer)==4,"stock timer");
volatile struct r1_spo2_timing_state r1_spo2_timing_state
    __attribute__((section(".r1.spo2.timing.state"),aligned(4)))={2,0,0,0,0};
volatile uint32_t r1_spo2_streams[3]
    __attribute__((section(".bss.r1.spo2.streams"),aligned(4)))={0};
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);

/* Recovered name retained; this entry releases the shared SpO2 timer. */
__attribute__((section(".text.r1_stress_stream_release")))
void r1_stress_stream_release(void)
{
    uint32_t timer=r1_spo2_timing_state.timer;
    if (timer) {
        (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
        r1_spo2_timing_state.timer=0;
    }
}
__attribute__((section(".text.r1_native_health_group1_a_callback")))
void r1_native_health_group1_a_callback(void)
{
    uint32_t handle=r1_spo2_streams[1];
    if (handle) {
        r1_sensor_stream_unregister_by_name("spo2",handle);
        r1_spo2_streams[1]=0;
    }
    r1_stress_stream_release();
    r1_spo2_timing_state.flag1=0;
    r1_spo2_timing_state.flag2=0;
    if (r1_spo2_timing_state.mode==1)
        r1_spo2_timing_start_plan(1);
}
__attribute__((section(".text.r1_native_health_group4_a_callback")))
void r1_native_health_group4_a_callback(const volatile void *event)
{
    if (*(const volatile uint8_t *)event==1) return;
    for (uint32_t i=0;i<2;i++) {
        uint32_t handle=r1_spo2_streams[i];
        if (handle) {
            r1_sensor_stream_unregister_by_name("spo2",handle);
            r1_spo2_streams[i]=0;
        }
    }
    r1_stress_stream_release();
}
