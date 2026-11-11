#include <stdint.h>
extern volatile uint8_t r1_health_mode_byte;
volatile int8_t r1_wear_charge_status __attribute__((section(".bss.r1.wear.charge.status")));
volatile uint32_t r1_wear_charge_timer __attribute__((section(".r1.wear.charge.timer"),aligned(4)))=0;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void r1_wear_probe_teardown(void);
extern uint32_t r1_wear_raw_hr_probe_start(void),r1_state_byte_nonzero_96a40(uint32_t);
extern uint32_t r1_event_service_0008b028(uint32_t,const void *,uint32_t);
extern uint32_t r1_stream_timer_release(uint32_t),r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern void r1_wear_charge_timer_callback(uint32_t);

/* Stock 0x4c4b8 compares a sign-extended old byte with the full request. */
void r1_wear_charge_set(uint32_t status)
{
    if ((uint32_t)(int32_t)r1_wear_charge_status==status) return;
    r1_wear_charge_status=(int8_t)status;
    const char *ring="[RING]algo wear charge status: %d";
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,ring,ring,status);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"algo wear charge status: %d",status);
    uint8_t event;
    if (status==1) {
        r1_wear_probe_teardown();
        (void)r1_wear_raw_hr_probe_start();
        event=(uint8_t)r1_state_byte_nonzero_96a40(0);
        (void)r1_event_service_0008b028(4,&event,1);
        if (!r1_wear_charge_timer)
            r1_wear_charge_timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_wear_charge_timer_callback,60000,0);
    } else {
        uint32_t timer=r1_wear_charge_timer;
        if (timer) {(void)r1_stream_timer_release(timer);r1_wear_charge_timer=0;}
        event=(uint8_t)r1_state_byte_nonzero_96a40(r1_health_mode_byte);
        (void)r1_event_service_0008b028(4,&event,1);
    }
}
extern void r1_event_service_0004c4b8(uint32_t) __attribute__((alias("r1_wear_charge_set")));
