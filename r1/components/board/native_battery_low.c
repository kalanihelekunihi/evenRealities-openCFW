#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_device_context[];
extern void *volatile r1_low_battery_thread_handle;
extern uint32_t r1_structured_log_mode_get(void),r1_battery_voltage_get(void),time_backend_timestamp_thunk(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void r1_kv_dev_info_fields_set(volatile void *);
extern uint32_t osThreadFlagsSet(void *,uint32_t),r1_event_publish(uint32_t,const void *,uint32_t);
const char r1_battery_low_ring[] __attribute__((section(".r1.battery_low.ring")))="[RING]battery voltage low %d(3350mv), low_power_cnt=%d";
const char r1_battery_low_sdk[] __attribute__((section(".r1.battery_low.sdk")))="battery voltage low %d(3350mv), low_power_cnt=%d";
/* Native0x3d88c saves incoming r2/r3 as the two-word event record.
 * Ring logging replaces word0; escalation replaces timestamp and low16 bits.
 * The count9 event path instead forwards through the event provider boundary. */
__attribute__((noinline)) void r1_battery_low_escalation(void)
{
    uint32_t incoming2,incoming3;
    __asm__ volatile("mov %0, r2\nmov %1, r3" : "=r"(incoming2),"=r"(incoming3) : : "r2","r3");
    volatile uint32_t record[2]={incoming2,incoming3};
    volatile uint8_t *d=r1_battery_device_context;
    if (read16(d+42)>=3350u) { d[47]=0;goto done; }
    d[47]=(uint8_t)(d[47]+1u);
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        uint32_t count=d[47];record[0]=count;
        r1_structured_log_format(0x08800000,r1_battery_low_ring,r1_battery_low_ring,(uint32_t)read16(d+42),count);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t count=d[47],voltage=read16(d+42);
        nrf_log_frontend_std_2(0x001c0002,r1_battery_low_sdk,voltage,count);
    }
    uint32_t count=d[47];
    if (count==9) { (void)r1_event_publish(0x100c,0,0);return; }
    if (count>=10) {
        record[1]&=0xfffffffcu;
        uint32_t voltage=r1_battery_voltage_get();
        record[1]=(record[1]&0xffff0003u)|((voltage&0x3fffu)<<2);
        record[0]=time_backend_timestamp_thunk();
        r1_kv_dev_info_fields_set(record);
        (void)osThreadFlagsSet(r1_low_battery_thread_handle,1);
    }
done:;
    uint32_t restored2=record[0],restored3=record[1];
    __asm__ volatile("mov r2, %0\nmov r3, %1" : : "r"(restored2),"r"(restored3) : "r2","r3");
}
