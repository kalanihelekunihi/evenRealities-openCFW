#include "native_health_hr_timing.h"
#include "native_health_hr_control.h"
#include "native_hrv_timing.h"
extern volatile uint32_t r1_health_hr_streams[5];
extern uint32_t r1_health_mode_get(void),r1_cfg_byte_get_73798(void),r1_health_mode_is_2(void);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t),r1_stream_timer_release(uint32_t);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern void r1_spo2_timing_start_plan(uint32_t),r1_hr_stream_release(void);
extern uint32_t r1_time_backend_timestamp(void),r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
/* Keep the five-argument outgoing area out of the NV gate's caller frame. */
__attribute__((noinline)) static uint32_t register_timing(void)
{return r1_sensor_stream_register_by_name("hr","timing",(uintptr_t)r1_hr_timing_result_plan,1,1);}
/* Eight-byte C gate frame keeps the NV getter at the native caller depth. */
__attribute__((noinline)) static uint32_t timing_health_enabled(void)
{return r1_cfg_byte_get_73798()!=0;}
void r1_hr_timing_timer_callback(uint32_t timer)
{
    (void)timer;
    if(!r1_health_mode_get() || !timing_health_enabled())return;
    if(!r1_health_hr_streams[1]){
        uint32_t stream=register_timing();
        r1_health_hr_streams[1]=stream;
        if(stream && !r1_hrv_timing_state.hr_timer)
            r1_hrv_timing_state.hr_timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_algo_hr_timing_timeout,120000,0);
    }
    (void)r1_gomore_authorization_dispatch_native(5,1);
    r1_hrv_timing_start_plan(0);
    r1_spo2_timing_start_plan(0);
}
void r1_hr_timing_result_plan(uint32_t handle,const volatile void *input,uint32_t length)
{
    (void)length;
    const volatile uint8_t *sample=input;
    const char *ring="[RING]algo hr timing result: hr:%d, con:%d, sig:%d";
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0cc00000,ring,ring,sample[0],sample[1],sample[2]);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003,"algo hr timing result: hr:%d, con:%d, sig:%d",sample[0],sample[1],sample[2]);
    if(r1_hr_value_plausible(sample) && r1_health_mode_is_2()){
        uint32_t packet[2]={sample[0],0};
        packet[1]=r1_time_backend_timestamp();
        (void)r1_event_publish(6,packet,8);
    }
    r1_sensor_stream_unregister_by_name("hr",handle);
    r1_health_hr_streams[1]=0;
    r1_hr_stream_release();
}
void r1_algo_hr_timing_timeout(uint32_t timer)
{
    const char *ring="[RING]algo hr timing timeout";
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"algo hr timing timeout");
    uint32_t handle=r1_health_hr_streams[1];
    if(handle){r1_sensor_stream_unregister_by_name("hr",handle);r1_health_hr_streams[1]=0;}
    (void)r1_gomore_authorization_dispatch_native(5,0);
    (void)r1_stream_timer_release(timer);
    r1_hrv_timing_state.hr_timer=0;
}
