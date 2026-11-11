#include "native_sleep_wake.h"
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_event_service_0008b028(uint32_t,const void *,uint32_t);
extern void r1_algo_sleep_vivo_probe_start(void);
void r1_algo_sleep_result_report(uint32_t status)
{
    volatile uint32_t packet=status;
    const char *ring="[RING]algo sleep result: status:%d";
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,ring,ring,(uint8_t)packet);
    if(r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"algo sleep result: status:%d",(uint8_t)packet);
    uint32_t first_active=(uint8_t)packet==1 && r1_sleep_wake_control.active==0;
    r1_sleep_wake_control.active=(uint8_t)packet;
    (void)r1_event_publish(12,(const void *)&packet,1);
    (void)r1_event_service_0008b028(3,(const void *)&packet,1);
    if(first_active)r1_algo_sleep_vivo_probe_start();
}
