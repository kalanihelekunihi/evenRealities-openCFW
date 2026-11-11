#include <stdint.h>
#include "native_gomore_authorization.h"
volatile struct r1_gomore_sensor_state r1_gomore_sensor_state
    __attribute__((section(".bss.r1.gomore.sensor.state"),aligned(4)));
extern uint32_t r1_time_backend_timestamp(void),r1_health_mode_get(void);
extern int32_t r1_time_utc_offset_get(void);
extern uint32_t r1_gomore_sensor_update_native(volatile void *);
extern void r1_record12_reinitialize(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
uint32_t r1_gomore_sensor_stamp_time(void)
{
    r1_gomore_sensor_state.timestamp=r1_time_backend_timestamp();
    r1_gomore_sensor_state.utc_offset=(uint16_t)r1_time_utc_offset_get();
    r1_gomore_sensor_state.time_valid=1;
    uint32_t inactive=r1_health_mode_get()==0;
    r1_gomore_sensor_state.inactive=(uint8_t)inactive;
    return inactive;
}
uint32_t r1_gomore_sensor_update_complete(void)
{
    r1_gomore_sensor_state.raw_hr_count=0;
    r1_gomore_sensor_state.acc_count=0;
    return (uint32_t)(uintptr_t)&r1_gomore_sensor_state;
}
uint32_t r1_gomore_sensor_failure_update(uint32_t status)
{
    if (!status) {
        r1_gomore_authorization_state.padding0[2]=0;
        return 1;
    }
    if (r1_gomore_authorization_state.padding0[2]<3) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04800000,
                "[RING]gomore updateIndex failed:%d, ts:%d",
                "[RING]gomore updateIndex failed:%d, ts:%d",status,r1_gomore_sensor_state.timestamp);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x001c0001,"gomore updateIndex failed:%d, ts:%d",status,r1_gomore_sensor_state.timestamp);
    }
    uint32_t failures=(uint8_t)(r1_gomore_authorization_state.padding0[2]+1u);
    r1_gomore_authorization_state.padding0[2]=(uint8_t)failures;
    if (failures>=60) {
        r1_gomore_authorization_state.padding0[2]=0;
        r1_record12_reinitialize();
    }
    return 0;
}
uint32_t r1_gomore_idle_timer_callback(uint32_t context)
{
    (void)context;
    (void)r1_gomore_sensor_stamp_time();
    uint32_t status=r1_gomore_sensor_update_native(&r1_gomore_sensor_state);
    if (r1_gomore_sensor_failure_update(status)) return r1_gomore_sensor_update_complete();
    return 0;
}
