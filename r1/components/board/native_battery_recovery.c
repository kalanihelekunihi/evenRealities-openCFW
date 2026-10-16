#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_device_context[],r1_battery_runtime_context[];
extern uint32_t osKernelGetTickCount(void),osKernelGetTickFreq(void);
extern void r1_battery_charging_progress_reset(void);
extern uint32_t r1_battery_charging_initial_curve(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_battery_recovery_ring[] __attribute__((section(".r1.battery_recovery.ring")))="[RING]battery v2 stuck recover: pct=%u mV ref=%u now=%u tick=%u";
const char r1_battery_recovery_sdk[] __attribute__((section(".r1.battery_recovery.sdk")))="battery v2 stuck recover: pct=%u mV ref=%u now=%u tick=%u";
/* Native0x3db70 restores its three saved argument words, including values
 * overwritten by stack log arguments. Preserve this selected register ABI. */
__attribute__((noinline)) void r1_battery_stuck_charge_recovery(uint32_t state,volatile void *timestamp)
{
    uint32_t incoming2,incoming3;
    __asm__ volatile("mov %0, r2\nmov %1, r3" : "=r"(incoming2),"=r"(incoming3) : : "r2","r3");
    volatile uint32_t saved[3]={(uint32_t)(uintptr_t)timestamp,incoming2,incoming3};
    volatile uint8_t *d=r1_battery_device_context,*b=r1_battery_runtime_context,*stamp=timestamp;
    if (state!=1) { b[3]=255;b[4]=0;goto done; }
    uint32_t now=osKernelGetTickCount();
    uint32_t frequency=osKernelGetTickFreq();
    if (!frequency) goto done;
    uint32_t level=d[44];
    if (!level) goto done;
    uint32_t previous=b[3];
    if (previous==255) {
        write32(b+32,now);write16(b+10,read16(d+42));b[3]=(uint8_t)level;goto done;
    }
    if (level!=previous) {
        b[3]=(uint8_t)level;write32(b+32,now);write16(b+10,read16(d+42));b[4]=0;goto done;
    }
    if (b[4] || level>=99) goto done;
    uint32_t reference=read16(b+10);
    if (reference<2400) goto done;
    uint32_t voltage=read16(d+42);
    if (voltage<2400 || voltage<reference+35u) goto done;
    uint32_t elapsed=now-read32(b+32);
    if ((uint64_t)elapsed<(uint64_t)frequency*120u) goto done;
    r1_battery_charging_progress_reset();
    uint32_t estimate=r1_battery_charging_initial_curve(read16(d+42));
    level=d[44];if (level<estimate) level=estimate;
    if (level>100) level=100;
    d[48]=(uint8_t)level;
    if (!read32(stamp)) write32(stamp,now);
    reference=read16(b+10);b[4]=1;write32(b+32,now);write16(b+10,read16(d+42));
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        uint32_t voltage_now=read16(d+42),tick=read32(stamp);
        saved[0]=reference;saved[1]=voltage_now;saved[2]=tick;
        r1_structured_log_format(0x09000000,r1_battery_recovery_ring,r1_battery_recovery_ring,(uint32_t)d[44],reference,voltage_now,tick);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t tick=read32(stamp),voltage_now=read16(d+42);
        saved[0]=voltage_now;saved[1]=tick;
        nrf_log_frontend_std_4(0x001c0002,r1_battery_recovery_sdk,d[44],reference,voltage_now,tick);
    }
done:;
    uint32_t restored1=saved[0],restored2=saved[1],restored3=saved[2];
    __asm__ volatile("mov r1, %0\nmov r2, %1\nmov r3, %2" : : "r"(restored1),"r"(restored2),"r"(restored3) : "r1","r2","r3");
}
