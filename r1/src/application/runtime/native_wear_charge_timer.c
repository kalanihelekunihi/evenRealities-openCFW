#include <stdint.h>
extern volatile int8_t r1_wear_charge_status;
extern volatile uint32_t r1_wear_charge_timer;
extern volatile uint8_t r1_health_mode_byte;
extern uint32_t r1_native_charger_state_get(void),r1_charge_state_byte_get(void);
extern uint32_t r1_proto_report_battery_status(uint32_t,uint32_t),r1_glasses_tag_frame_send(uint32_t,uint32_t);
extern uint32_t r1_battery_task_flags_set(uint32_t),r1_state_byte_nonzero_96a40(uint32_t);
extern uint32_t r1_event_service_0008b028(uint32_t,const void *,uint32_t),r1_stream_timer_release(uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);

/* Stock 0x4c3d0: poll charge, then publish/report before releasing the timer. */
void r1_wear_charge_timer_callback(uint32_t context)
{
    (void)context;
    uint32_t charge=r1_native_charger_state_get();
    const char *ring="[RING]algo wear charge check: %d";
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,ring,ring,charge);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"algo wear charge check: %d",charge);
    if (charge || (uint8_t)r1_wear_charge_status!=1) return;
    uint8_t event=(uint8_t)r1_state_byte_nonzero_96a40(r1_health_mode_byte);
    (void)r1_event_service_0008b028(4,&event,1);
    (void)r1_proto_report_battery_status(r1_charge_state_byte_get(),0);
    (void)r1_glasses_tag_frame_send(r1_charge_state_byte_get(),0);
    (void)r1_battery_task_flags_set(4096);
    uint32_t timer=r1_wear_charge_timer;
    if (timer) {(void)r1_stream_timer_release(timer);r1_wear_charge_timer=0;}
    r1_wear_charge_status=0;
}
