#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_device_context[],r1_battery_runtime_context[];
extern uint32_t osKernelGetTickCount(void),osKernelGetTickFreq(void),r1_batcfg_byte0_get(void);
uint32_t r1_battery_charging_cadence(uint32_t voltage,uint32_t timestamp)
{
    volatile uint8_t *d=r1_battery_device_context,*state=d+52;
    uint32_t initial=d[48];
    if (initial>=100) return 100;
    if (!timestamp) return initial;
    if (read32(state)!=timestamp) {
        write32(state,timestamp);state[8]=(uint8_t)initial;write32(state+12,0);
        write32(state+4,osKernelGetTickCount());
    }
    uint32_t now=osKernelGetTickCount();
    uint32_t elapsed=now-read32(state+4);
    uint32_t frequency=osKernelGetTickFreq();
    uint32_t seconds=frequency ? elapsed/frequency:0;
    if (seconds>180) seconds=180;
    write32(state+4,now);write32(state+12,read32(state+12)+seconds);
    uint32_t kind=r1_batcfg_byte0_get();
    volatile uint8_t *table=r1_battery_runtime_context+44;
    if (kind-1u<4u) table+=(kind-1u)*12u;
    for (;;) {
        uint32_t level=state[8];
        if (level>=100) break;
        uint32_t remaining=read32(state+12);
        if (!remaining) break;
        uint32_t offset=level<85 ? 0:level<90 ? 2:level<95 ? 4:6;
        uint32_t interval=read16(table+offset);
        if (!interval) break;
        if (remaining<interval) break;
        write32(state+12,remaining-interval);state[8]=(uint8_t)(level+1u);
    }
    if (voltage>4340u && d[46]>4u) return 100;
    return state[8];
}
