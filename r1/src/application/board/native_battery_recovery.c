#include <stdint.h>
#include "native_battery_context.h"
#include "native_battery_memory.h"
extern uint32_t osKernelGetTickCount(void),osKernelGetTickFreq(void);
extern void r1_battery_charging_progress_reset(void);
extern uint32_t r1_battery_charging_initial_curve(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_battery_recovery_ring[] __attribute__((section(".r1.battery_recovery.ring")))="[RING]battery v2 stuck recover: pct=%u mV ref=%u now=%u tick=%u";
const char r1_battery_recovery_sdk[] __attribute__((section(".r1.battery_recovery.sdk")))="battery v2 stuck recover: pct=%u mV ref=%u now=%u tick=%u";
/* Recovery uses the public void C ABI. Device/runtime memory remains volatile;
 * incidental saved argument words and logger-private stack aliases are retired. */
static inline volatile uint8_t *r1_battery_recovery_device_bytes(void) {
 return r1_battery_device_context;
}
void r1_battery_stuck_charge_recovery(uint32_t state,volatile void *timestamp)
{
    volatile uint8_t *b=r1_battery_runtime_context;
    volatile uint8_t *stamp=timestamp;
    uint32_t now,reference;
    volatile uint8_t *device;
    if (state!=1) { b[3]=255;b[4]=0;return; }
    now=osKernelGetTickCount();
    uint32_t frequency=osKernelGetTickFreq();
    if (!frequency) return;
    uint32_t level=r1_battery_recovery_device_bytes()[44];
    if (!level) return;
    uint32_t previous=b[3];
    if (previous==255) {
        write32(b+32,now);write16(b+10,read16(r1_battery_recovery_device_bytes()+42));b[3]=(uint8_t)level;return;
    }
    if (level!=previous) {
        b[3]=(uint8_t)level;write32(b+32,now);write16(b+10,read16(r1_battery_recovery_device_bytes()+42));b[4]=0;return;
    }
    if (b[4] || level>=99) return;
    reference=read16(b+10);
    if (reference<2400) return;
    uint32_t voltage=read16(r1_battery_recovery_device_bytes()+42);
    if (voltage<2400 || voltage<reference+35u) return;
    uint32_t elapsed=now-read32(b+32);
    if ((uint64_t)elapsed<(uint64_t)frequency*120u) return;
    device=r1_battery_recovery_device_bytes();r1_battery_charging_progress_reset();
    uint32_t estimate=r1_battery_charging_initial_curve(read16(device+42));
    level=device[44];if (level<estimate) level=estimate;
    if (level>100) level=100;
    device[48]=(uint8_t)level;
    if (!read32(stamp)) write32(stamp,now);
    reference=read16(b+10);b[4]=1;write32(b+32,now);write16(b+10,read16(device+42));
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        uint32_t voltage_now=read16(device+42),tick=read32(stamp);
        r1_structured_log_format(0x09000000,r1_battery_recovery_ring,r1_battery_recovery_ring,(uint32_t)device[44],reference,voltage_now,tick);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t tick=read32(stamp),voltage_now=read16(device+42);
        nrf_log_frontend_std_4(0x001c0002,r1_battery_recovery_sdk,device[44],reference,voltage_now,tick);
    }
}
