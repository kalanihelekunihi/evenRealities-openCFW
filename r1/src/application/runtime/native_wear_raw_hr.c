#include <stdint.h>

/* Only the two authenticated words at 20006eac and 20006eb0 are owned. */
volatile uint32_t r1_wear_raw_hr_stream_handle
    __attribute__((section(".r1.wear.raw_hr.stream"),aligned(4)))=0;
volatile uint32_t r1_wear_raw_hr_timer
    __attribute__((section(".r1.wear.raw_hr.timer"),aligned(4)))=0;
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern uint32_t r1_stream_timer_rearm_native(uint32_t);

__attribute__((section(".text.r1_wear_raw_hr_sample_ignore")))
void r1_wear_raw_hr_sample_ignore(void) {}

__attribute__((section(".text.r1_raw_hr_stream_teardown")))
void r1_raw_hr_stream_teardown(void)
{
    uint32_t stream=r1_wear_raw_hr_stream_handle;
    if (stream) {
        r1_sensor_stream_unregister_by_name("raw_hr",stream);
        r1_wear_raw_hr_stream_handle=0;
    }
    uint32_t timer=r1_wear_raw_hr_timer;
    if (timer) {
        (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
        r1_wear_raw_hr_timer=0;
    }
}

__attribute__((section(".text.r1_wear_raw_hr_probe_start")))
uint32_t r1_wear_raw_hr_probe_start(void)
{
    if (!r1_wear_raw_hr_stream_handle) {
        uint32_t stream=r1_sensor_stream_register_by_name("raw_hr","wearled",
            (uintptr_t)r1_wear_raw_hr_sample_ignore,1,0);
        r1_wear_raw_hr_stream_handle=stream;
    }
    uint32_t timer=r1_wear_raw_hr_timer;
    if (timer) return r1_stream_timer_rearm_native(timer);
    timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_raw_hr_stream_teardown,3000,0);
    r1_wear_raw_hr_timer=timer;
    return timer;
}
