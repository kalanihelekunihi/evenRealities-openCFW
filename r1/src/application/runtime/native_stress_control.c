#include "native_stress_control.h"
_Static_assert(sizeof(struct r1_stress_mode_control)==8,"native stress mode state");
volatile struct r1_stress_mode_control r1_stress_mode_control __attribute__((section(".r1.stress.mode.control"),aligned(4)))={2,{0},0};
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern uint32_t r1_stream_timer_release(uint32_t),r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
uint32_t r1_stress_enable(uint32_t enabled,uint32_t length)
{(void)length;return r1_gomore_authorization_dispatch_native(1,enabled);}
void r1_stress_periodic_timer_callback(uint32_t timer)
{(void)timer;(void)r1_stress_enable(1,0);}
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
void r1_stress_mode_timer_plan(uint32_t old_mode,uint32_t new_mode)
{
    if(old_mode==new_mode){
        const char *ring="[RING]stress mode is same";
        if(ring_enabled())(void)r1_structured_log_format(0x0c000000,ring,ring);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"stress mode is same");
        return;
    }
    if(old_mode==1){
        uint32_t timer=r1_stress_mode_control.timer;
        if(timer){(void)r1_stream_timer_release(timer);r1_stress_mode_control.timer=0;}
    }
    if(new_mode==1 && !r1_stress_mode_control.timer){
        r1_stress_mode_control.timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_stress_periodic_timer_callback,3600000,0);
        const char *ring="[RING]algo stress timing mode timer %d create";
        if(ring_enabled())(void)r1_structured_log_format(0x0c400000,ring,ring,3600u);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,"algo stress timing mode timer %d create",3600u);
    }
}
void r1_stress_mode_set(uint32_t mode,uint32_t length)
{
    (void)length;
    if(mode>=2)return;
    r1_stress_mode_timer_plan(r1_stress_mode_control.mode,mode);
    r1_stress_mode_control.mode=(uint8_t)mode;
}
extern uint32_t r1_event_service_0004b33e(uint32_t,uint32_t) __attribute__((alias("r1_stress_enable")));
extern void r1_event_service_0004b48c(uint32_t,uint32_t) __attribute__((alias("r1_stress_mode_set")));
