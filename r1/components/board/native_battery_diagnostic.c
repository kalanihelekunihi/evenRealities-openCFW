#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_device_context[];
extern uint32_t r1_batcfg_byte0_get(void),r1_batcfg_word1_signed_get(void),r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_battery_diagnostic_period_ring[] __attribute__((section(".r1.battery_diagnostic.period_ring")))="[RING]battery:%d, voltage:%d, status:%d, type:%d";
const char r1_battery_diagnostic_period_sdk[] __attribute__((section(".r1.battery_diagnostic.period_sdk")))="battery:%d, voltage:%d, status:%d, type:%d";
const char r1_battery_diagnostic_offset_ring[] __attribute__((section(".r1.battery_diagnostic.offset_ring")))="[RING]voltage_compensation:%d";
const char r1_battery_diagnostic_offset_sdk[] __attribute__((section(".r1.battery_diagnostic.offset_sdk")))="voltage_compensation:%d";
const char r1_battery_diagnostic_charge_ring[] __attribute__((section(".r1.battery_diagnostic.charge_ring")))="[RING]charge_start: tick=%u, voltage=%d; charge_end: tick=%u, voltage=%d";
const char r1_battery_diagnostic_charge_sdk[] __attribute__((section(".r1.battery_diagnostic.charge_sdk")))="charge_start: tick=%u, voltage=%d; charge_end: tick=%u, voltage=%d";
void r1_battery_diagnostic_cadence_step(volatile void *counter,uint32_t timestamp,uint32_t start_voltage,uint32_t tracking_tick,uint32_t reference_voltage,uint32_t state)
{
    volatile uint8_t *count=counter,*d=r1_battery_device_context;
    uint8_t next=(uint8_t)(*count+1u);*count=next;
    if (next%5u==0) {
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
            uint32_t kind=r1_batcfg_byte0_get(),voltage=read16(d+42),level=d[44];
            r1_structured_log_format(0x0d000000,r1_battery_diagnostic_period_ring,r1_battery_diagnostic_period_ring,level,voltage,state,kind);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t kind=r1_batcfg_byte0_get(),voltage=read16(d+42),level=d[44];
            nrf_log_frontend_std_4(0x001c0003,r1_battery_diagnostic_period_sdk,level,voltage,state,kind);
        }
    }
    if (*count>=30u) {
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
            uint32_t offset=r1_batcfg_word1_signed_get();
            r1_structured_log_format(0x0c400000,r1_battery_diagnostic_offset_ring,r1_battery_diagnostic_offset_ring,offset);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t offset=r1_batcfg_word1_signed_get();
            nrf_log_frontend_std_1(0x001c0003,r1_battery_diagnostic_offset_sdk,offset);
        }
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x0d000000,r1_battery_diagnostic_charge_ring,r1_battery_diagnostic_charge_ring,timestamp,start_voltage,tracking_tick,reference_voltage);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_4(0x001c0003,r1_battery_diagnostic_charge_sdk,timestamp,start_voltage,tracking_tick,reference_voltage);
        *count=0;
    }
}
