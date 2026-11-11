#include <stdint.h>
#include "native_hrv_timing.h"
#include "../board/native_battery_memory.h"
extern volatile uint32_t r1_health_hr_streams[5];
#include "native_health_hr_timing.h"
extern void r1_hr_stream_release(void),r1_hr_session_teardown(void);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_release(uint32_t),r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
void r1_hr_mode_transition(uint32_t old_mode,uint32_t new_mode)
{
    if(old_mode==new_mode){
        const char *ring="[RING]heartrate mode is same";
        if(ring_enabled())(void)r1_structured_log_format(0x0c000000,ring,ring);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"heartrate mode is same");
        return;
    }
    /* Preserve stock wrapping address calculation, including initial mode 4. */
    volatile uint8_t *slot=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)r1_health_hr_streams+(old_mode<<2));
    uint32_t handle=read32(slot);
    if(handle){r1_sensor_stream_unregister_by_name("hr",handle);write32(slot,0);}
    if(old_mode==1){
        uint32_t timer=r1_hrv_timing_state.field8;
        if(timer){(void)r1_stream_timer_release(timer);r1_hrv_timing_state.field8=0;}
        r1_hr_stream_release();
        if(r1_hrv_timing_state.timer){r1_hr_session_teardown();r1_hrv_stream_release();}
        r1_hrv_timing_state.flag1=0;r1_hrv_timing_state.flag2=0;
    }
    if(new_mode==1 && !r1_hrv_timing_state.field8){
        r1_hrv_timing_state.field8=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_hr_timing_timer_callback,600000,0);
        const char *ring="[RING]algo hr timing mode timer %d create";
        if(ring_enabled())(void)r1_structured_log_format(0x0c400000,ring,ring,600u);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,"algo hr timing mode timer %d create",600u);
    }
}
void r1_hr_mode_set(uint32_t mode,uint32_t length)
{
    (void)length;
    if(mode>=4)return;
    r1_hr_mode_transition(r1_hrv_timing_state.mode,mode);
    r1_hrv_timing_state.mode=(uint8_t)mode;
}
extern void r1_event_service_000499c4(uint32_t,uint32_t) __attribute__((alias("r1_hr_mode_set")));
