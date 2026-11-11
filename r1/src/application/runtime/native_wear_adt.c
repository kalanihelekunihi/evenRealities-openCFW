#include <stdint.h>

volatile uint8_t r1_wear_adt_status __attribute__((section(".r1.wear.adt.status")))=1;
volatile uint32_t r1_wear_adt_stream __attribute__((section(".r1.wear.adt.stream"),aligned(4)))=0;
volatile uint32_t r1_wear_adt_timer __attribute__((section(".r1.wear.adt.timer"),aligned(4)))=0;
volatile uint8_t r1_wear_adt_active __attribute__((section(".bss.r1.wear.adt.active")));
volatile uint32_t r1_wear_adt_count __attribute__((section(".bss.r1.wear.adt.count"),aligned(4)));
volatile uint8_t r1_wear_adt_sleep_gate __attribute__((section(".bss.r1.wear.adt.sleep_gate")));
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern void r1_wear_adt_sample_native(uint32_t,uint32_t,uint32_t);
extern void r1_wear_adt_timeout_native(void);

__attribute__((section(".text.r1_wear_probe_teardown")))
void r1_wear_probe_teardown(void)
{
    uint32_t stream=r1_wear_adt_stream;
    if (stream) {
        r1_wear_adt_stream=0;
        r1_sensor_stream_unregister_by_name("adt",stream);
    }
    r1_wear_adt_active=0;
    r1_wear_adt_count=0;
    uint32_t timer=r1_wear_adt_timer;
    if (timer) {
        r1_wear_adt_timer=0;
        (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
    }
}

__attribute__((section(".text.r1_wear_adt_status_topic_callback")))
void r1_wear_adt_status_topic_callback(uint32_t status)
{
    r1_wear_adt_status=(uint8_t)status;
    if (r1_wear_adt_sleep_gate==1) {
        r1_wear_probe_teardown();
        return;
    }
    uint32_t stream=r1_wear_adt_stream;
    if ((stream|status)!=0) {
        if (status==1) r1_wear_probe_teardown();
        return;
    }
    stream=r1_sensor_stream_register_by_name("adt","algo",
        (uintptr_t)r1_wear_adt_sample_native,1,1);
    r1_wear_adt_stream=stream;
    if (!r1_wear_adt_timer) {
        uint32_t timer=r1_stream_timer_create_front(
            (uint32_t)(uintptr_t)r1_wear_adt_timeout_native,7000,0);
        r1_wear_adt_timer=timer;
    }
}
