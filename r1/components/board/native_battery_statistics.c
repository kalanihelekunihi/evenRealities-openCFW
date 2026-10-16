#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_device_context[];
extern uint32_t osKernelGetTickCount(void);
extern void r1_shared_power_client_acquire(uint32_t),r1_battery_charging_progress_reset(void);
uint32_t r1_battery_charged_state_refresh(uint32_t state,volatile void *start,volatile void *start_voltage,volatile void *stop,volatile void *stop_voltage)
{
    volatile uint8_t *d=r1_battery_device_context;
    if (state==1) {
        d[46]=0;
        if (!d[45]) {
            uint32_t tick=osKernelGetTickCount();write32(start,tick ? tick:1);
            uint16_t voltage=read16(d+42);write16(start_voltage,voltage);write16(d+49,read16(d+42));
            d[48]=d[44];
        }
        d[45]=1;return 1;
    }
    if (d[45]==1) { uint32_t tick=osKernelGetTickCount();write32(stop,tick);write16(stop_voltage,read16(d+42)); }
    if (state==2) { d[45]=0;if (d[46]<8) d[46]=(uint8_t)(d[46]+1u); }
    else { d[46]=0;d[45]=0; }
    r1_shared_power_client_acquire(0);r1_battery_charging_progress_reset();return 0;
}
uint32_t r1_battery_level_average(void)
{
    uint32_t sum=0,count=0,minimum=65535,maximum=0;
    for (uint32_t i=0;i<8;i++) {
        uint32_t value=r1_battery_device_context[34+i];
        if (value) { sum+=value;count++;if (value<minimum)minimum=value;if (value>maximum)maximum=value; }
    }
    if (count==8) return (uint8_t)((sum-minimum-maximum+3u)/6u);
    return count ? (uint8_t)(sum/count):0;
}
void r1_battery_voltage_average(void)
{
    volatile uint8_t *d=r1_battery_device_context;
    uint32_t sum=0,count=0,minimum=65535,maximum=0;
    for (uint32_t i=0;i<8;i++) {
        uint32_t value=read16(d+18+i*2);
        if (value) { sum+=value;count++;if (value<minimum)minimum=value;if (value>maximum)maximum=value; }
    }
    if (count==8) write16(d+42,(sum-minimum-maximum)/6u);
    else if (count) write16(d+42,sum/count);
}
