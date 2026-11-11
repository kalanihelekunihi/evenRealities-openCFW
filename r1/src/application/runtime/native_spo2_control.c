#include <stdint.h>
#include "native_spo2_timing.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern void r1_spo2_once_result_plan(uint32_t,const volatile void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
void r1_spo2_once_control(uint32_t enabled,uint32_t length)
{
    (void)length;
    if(enabled){
        if(!r1_spo2_streams[0])r1_spo2_streams[0]=r1_sensor_stream_register_by_name("spo2","once",(uintptr_t)r1_spo2_once_result_plan,1,1);
    }else if(r1_spo2_streams[0]){
        r1_sensor_stream_unregister_by_name("spo2",r1_spo2_streams[0]);
        r1_spo2_streams[0]=0;
    }
}
void r1_spo2_mode_transition(uint32_t old_mode,uint32_t new_mode)
{
    if(old_mode==new_mode){
        const char *ring="[RING]spo2 mode is same";
        if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x0c000000,ring,ring);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"spo2 mode is same");
        return;
    }
    volatile uint8_t *slot=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)r1_spo2_streams+(old_mode<<2));
    uint32_t handle=read32(slot);
    if(handle){r1_sensor_stream_unregister_by_name("spo2",handle);write32(slot,0);}
    if(old_mode==1){
        r1_stress_stream_release();
        r1_spo2_timing_state.flag1=0;r1_spo2_timing_state.flag2=0;
    }
}
void r1_spo2_mode_set(uint32_t mode,uint32_t length)
{
    (void)length;
    if(mode>=2)return;
    r1_spo2_mode_transition(r1_spo2_timing_state.mode,mode);
    r1_spo2_timing_state.mode=(uint8_t)mode;
}
extern void r1_event_service_0004aaf8(uint32_t,uint32_t) __attribute__((alias("r1_spo2_once_control")));
extern void r1_event_service_0004ad7c(uint32_t,uint32_t) __attribute__((alias("r1_spo2_mode_set")));
