#include <stdint.h>
#include "native_hrv_timing.h"
extern volatile uint32_t r1_health_hr_streams[5];
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
#include "native_health_hr_control.h"
void r1_hr_once_measurement_control(uint32_t enabled,uint32_t length)
{
    (void)length;
    if(enabled){
        if(r1_health_hr_streams[0])return;
        if(!r1_hrv_timing_state.stream)
            r1_hrv_timing_state.stream=r1_sensor_stream_register_by_name("hrv","algo",(uintptr_t)r1_hrv_producer,1,1);
        r1_health_hr_streams[0]=r1_sensor_stream_register_by_name("hr","once",(uintptr_t)r1_hr_once_result_plan,1,1);
    }else{
        if(!r1_health_hr_streams[0])return;
        r1_sensor_stream_unregister_by_name("hr",r1_health_hr_streams[0]);
        r1_health_hr_streams[0]=0;
    }
}
extern void r1_event_service_000497cc(uint32_t,uint32_t) __attribute__((alias("r1_hr_once_measurement_control")));
