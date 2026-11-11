/* Native battery startup 0x912a8 and ship-mode diagnostic getter 0x73694.
 * Failed/short persistence reads retain deterministic zero-initialized bytes. */
#include <stdint.h>
#include "native_battery_context.h"
#include "native_battery_memory.h"
#include "native_kv_class.h"
extern void *volatile r1_device_info_record_kv_handle;
extern uint32_t r1_native_charger_state_get(void);
extern uint32_t r1_battery_runtime_update_service(void);
extern uint32_t r1_battery_charging_initial_curve(uint32_t);
extern void r1_battery_charging_progress_reset(void), r1_st25_delay_ms(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
const char r1_battery_ship_ring[]="[RING]shipmode ts:%d, type:%d, voltage:%d";
const char r1_battery_ship_sdk[]="shipmode ts:%d, type:%d, voltage:%d";
void r1_battery_ship_record_get(uint32_t output[2])
{
    if (!output) return;
    uint32_t record[13]={0};
    (void)r1_kv_class_read(r1_device_info_record_kv_handle,record,sizeof(record));
    output[0]=record[9];
    output[1]=record[10];
}
void r1_battery_initialize_000912a8(void)
{
    volatile uint8_t *device=r1_battery_device_context;
    for (unsigned i=0;i<51;++i) device[i]=0;
    uint32_t initial_state=r1_native_charger_state_get();
    for (unsigned i=0;i<8;++i) {
        (void)r1_battery_runtime_update_service();
        r1_st25_delay_ms(10);
    }
    if (initial_state==1) {
        device[48]=(uint8_t)r1_battery_charging_initial_curve(read16(device+42));
        r1_battery_charging_progress_reset();
        uint8_t level=device[48];
        if (!level) level=1;
        device[44]=level;
        for (unsigned i=0;i<8;++i) device[34+i]=level;
    }
    r1_battery_runtime_context[1]=1;
    uint32_t ship[2]={0};
    r1_battery_ship_record_get(ship);
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x08c00000,r1_battery_ship_ring,r1_battery_ship_ring,
                                ship[0],ship[1]&3u,(ship[1]>>2)&0x3fffu);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_3(0x001c0002,r1_battery_ship_sdk,
                              ship[0],ship[1]&3u,(ship[1]>>2)&0x3fffu);
}
