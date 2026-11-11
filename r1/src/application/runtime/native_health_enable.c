#include "native_health_enable.h"
#include "native_gomore_record8.h"
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
uint32_t r1_health_engine_enabled_update_native(uint32_t enabled)
{
    _Alignas(4) volatile uint8_t record[8]={0};
    (void)r1_gomore_record8_get_native(0,record);
    uint32_t current=record[5]==0;
    if(current==enabled)return current;
    record[5]=(uint8_t)(enabled^1u);
    return r1_gomore_record8_apply_native(record);
}
uint32_t r1_health_enable_update(uint32_t value,uint32_t length)
{
    (void)length;
    uint32_t enabled=value!=0;
    const char *ring="[RING]health enable update: %d";
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,ring,ring,value);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,"health enable update: %d",value);
    (void)r1_health_engine_enabled_update_native(enabled);
    (void)r1_gomore_authorization_dispatch_native(0,enabled);
    return r1_gomore_authorization_dispatch_native(3,enabled);
}
extern uint32_t r1_event_service_000496fc(uint32_t,uint32_t) __attribute__((alias("r1_health_enable_update")));
