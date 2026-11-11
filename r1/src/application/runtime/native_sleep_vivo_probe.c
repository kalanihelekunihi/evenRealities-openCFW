#include "native_sleep_wake.h"
/* Separate recovered word immediately after the existing eight-byte owner. */
volatile uint32_t r1_sleep_vivo_timer __attribute__((section(".r1.sleep.vivo.timer"),aligned(4)))=0;
extern uint32_t r1_health_mode_is_2(void),r1_health_mode_get(void);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t),r1_stream_timer_release(uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void r1_algo_sleep_force_awake(uint32_t,uint32_t);
static void log_probe(uint32_t stopped)
{
    const char *ring=stopped?"[RING]sleep vivo probe: not living, force awake":"[RING]algo sleep vivo probe start";
    const char *sdk=stopped?"sleep vivo probe: not living, force awake":"algo sleep vivo probe start";
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,sdk);
}
void r1_sleep_vivo_probe_stop(uint32_t timer)
{
    if(!r1_health_mode_get()){log_probe(1);r1_algo_sleep_force_awake(0,0);}
    if(r1_sleep_wake_control.reserved[0]){
        (void)r1_gomore_authorization_dispatch_native(5,0);
        r1_sleep_wake_control.reserved[0]=0;
    }
    (void)r1_stream_timer_release(timer);
    r1_sleep_vivo_timer=0;
}
void r1_algo_sleep_vivo_probe_start(void)
{
    if(r1_sleep_vivo_timer || r1_health_mode_is_2())return;
    r1_sleep_wake_control.reserved[0]=(uint8_t)r1_gomore_authorization_dispatch_native(5,1);
    uint32_t timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_sleep_vivo_probe_stop,5000,0);
    r1_sleep_vivo_timer=timer;
    if(timer){log_probe(0);return;}
    if(r1_sleep_wake_control.reserved[0]){
        (void)r1_gomore_authorization_dispatch_native(5,0);
        r1_sleep_wake_control.reserved[0]=0;
    }
}
