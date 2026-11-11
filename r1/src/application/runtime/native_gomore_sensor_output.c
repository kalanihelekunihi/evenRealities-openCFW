#include <stdint.h>
#include <stddef.h>
#include "native_gomore_authorization.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_gomore_sensor_stamp_time(void),r1_gomore_sensor_update_native(volatile void *),r1_gomore_sensor_failure_update(uint32_t),r1_gomore_sensor_update_complete(void);
extern void r1_activity_periodic_accumulator(volatile void *);
extern void gomore_primitives_noop_49e58(void);
extern void r1_algo_sleep_result_report(uint32_t);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern uint32_t r1_gomore_sleep_interval_dispatch_native(volatile uint32_t *,volatile void *);
extern void r1_gomore_final_sleep_record_publish_native(volatile uint32_t *,volatile void *);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static volatile uint8_t *workspace(void){return (volatile uint8_t *)&r1_gomore_sensor_state;}
static void period_log(uint32_t on)
{
    const char *ring=on?"[RING]Sleep Period On, %d":"[RING]Sleep Period Off, %d";
    const char *sdk=on?"Sleep Period On, %d":"Sleep Period Off, %d";
    if(ring_enabled())(void)r1_structured_log_format(0x0c400000,ring,ring,workspace()[112]);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,sdk,workspace()[112]);
}
static void allocation_log(void)
{
    const char *ring="[RING]gomore sensor_malloc failed";
    if(ring_enabled())(void)r1_structured_log_format(0x04000000,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,"gomore sensor_malloc failed");
}
uint32_t r1_gomore_sensor_output_dispatch_native(void)
{
    (void)r1_gomore_sensor_stamp_time();
    uint32_t status=r1_gomore_sensor_update_native(&r1_gomore_sensor_state);
    if(!r1_gomore_sensor_failure_update(status))return 0;
    for(uint32_t i=0;i<7;i++){
        if(!(r1_gomore_authorization_state.entries[i].flags&1u) || i>=4)continue;
        if(i==0){r1_activity_periodic_accumulator(workspace()+120);continue;}
        if(i==1)continue;
        if(i==2){(void)*(volatile float *)(volatile void *)(workspace()+168);gomore_primitives_noop_49e58();continue;}
        uint32_t flags=workspace()[112];
        if(flags&2u){period_log(1);r1_algo_sleep_result_report(1);}
        else if(flags&4u){
            period_log(0);r1_algo_sleep_result_report(0);
            if(workspace()[112]&8u){
                _Alignas(8) struct {volatile uint8_t bytes[88];volatile uint32_t count;} output;
                output.count=0;
                __aeabi_memclr((void *)output.bytes,88);
                void *payload=pvPortMalloc(2880);
                if(!payload){allocation_log();continue;}
                __aeabi_memclr(payload,2880);
                write32(output.bytes+8,(uint32_t)(uintptr_t)payload);
                (void)r1_gomore_sleep_interval_dispatch_native(&output.count,output.bytes);
                r1_gomore_final_sleep_record_publish_native(&output.count,output.bytes);
                vPortFree(payload);
            }
        }
        int32_t stage=(int8_t)workspace()[98];
        if(stage==(int32_t)(r1_gomore_authorization_state.entries[4].flags&1u))continue;
        if(stage==1){
            const char *ring="[RING]Sleep Stage PPG On";
            if(ring_enabled())(void)r1_structured_log_format(0x0c000000,ring,ring);
            if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"Sleep Stage PPG On");
        }
        (void)r1_gomore_authorization_dispatch_native(4,(r1_gomore_authorization_state.entries[4].flags&1u)?0:1);
    }
    return r1_gomore_sensor_update_complete();
}
