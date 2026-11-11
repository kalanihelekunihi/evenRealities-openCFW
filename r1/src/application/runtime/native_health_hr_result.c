#include "native_health_hr_control.h"
extern volatile uint32_t r1_health_hr_streams[5];
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_health_mode_is_2(void),r1_time_backend_timestamp(void),r1_event_publish(uint32_t,const void *,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
uint32_t r1_hr_value_plausible(const volatile void *input)
{
    const volatile uint8_t *sample=input;
    return (uint32_t)(sample[0]-40u)<181u;
}
void r1_hr_once_result_plan(uint32_t handle,const volatile void *input,uint32_t length)
{
    (void)length;
    const volatile uint8_t *sample=input;
    const char *ring="[RING]algo hr once result: hr:%d, con:%d, sig:%d";
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0cc00000,ring,ring,sample[0],sample[1],sample[2]);
    if(r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_3(0x001c0003,"algo hr once result: hr:%d, con:%d, sig:%d",sample[0],sample[1],sample[2]);
    if(r1_hr_value_plausible(sample) && r1_health_mode_is_2()){
        uint32_t packet[2]={sample[0],0};
        packet[1]=r1_time_backend_timestamp();
        (void)r1_event_publish(6,packet,8);
    }
    r1_sensor_stream_unregister_by_name("hr",handle);
    r1_health_hr_streams[0]=0;
}
