#include "native_sleep_wake.h"
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void r1_temp_sleep_status_report(uint32_t),r1_gomore_sleep_force_wake_native(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
void r1_algo_sleep_low_power(uint32_t payload,uint32_t length)
{
    (void)payload;(void)length;
    const char *ring="[RING]algo sleep low power event";
    if(ring_enabled())(void)r1_structured_log_format(0x0c000000,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"algo sleep low power event");
    if(r1_sleep_wake_control.active!=1)return;
    ring="[RING]algo sleep low power event, sleep status: %d";
    if(ring_enabled())(void)r1_structured_log_format(0x0c400000,ring,ring,r1_sleep_wake_control.active);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,"algo sleep low power event, sleep status: %d",r1_sleep_wake_control.active);
    r1_sleep_wake_control.active=0;
    r1_temp_sleep_status_report(0);
    r1_gomore_sleep_force_wake_native();
    (void)r1_event_publish(12,(const void *)&r1_sleep_wake_control.active,1);
}
extern void r1_event_service_0004a5bc(uint32_t,uint32_t) __attribute__((alias("r1_algo_sleep_low_power")));
