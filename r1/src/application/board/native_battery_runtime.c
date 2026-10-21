#include <stdint.h>
#include "native_battery_memory.h"
/* Product0x31fd0. State roots and lower hardware/algorithm providers remain
 * explicit gates; unaligned SRAM fields use native-width packed views. */
extern volatile uint8_t r1_battery_device_context[],r1_battery_runtime_context[];
extern uint32_t r1_native_charger_state_get(void);
extern uint32_t r1_native_charger_initialize(void);
extern uint32_t r1_battery_task_flags_set(uint32_t);
extern uint32_t r1_battery_charged_state_refresh(uint32_t,volatile void *,volatile void *,volatile void *,volatile void *);
extern uint32_t osKernelGetTickCount(void);
extern void r1_battery_charging_progress_reset(void);
extern uint32_t r1_battery_five_sample_filter_and_conversion(void),r1_batcfg_word1_signed_get(void);
extern void __aeabi_memclr(void *,uint32_t);
extern void r1_battery_voltage_average(void),r1_battery_stuck_charge_recovery(uint32_t,volatile void *);
extern uint32_t r1_battery_discharge_curve(uint32_t,uint32_t),r1_battery_charging_cadence(uint32_t,uint32_t),r1_battery_level_average(void);
extern void r1_battery_diagnostic_cadence_step(volatile void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_battery_low_escalation(void),r1_shared_power_client_release(uint32_t);
extern uint32_t r1_proto_report_battery_status(uint32_t,uint32_t);
extern uint32_t r1_glasses_tag_frame_send(uint32_t,uint32_t);
uint32_t r1_battery_runtime_update_service(void)
{
    volatile uint8_t *d=r1_battery_device_context,*b=r1_battery_runtime_context;
    uint32_t state=r1_native_charger_state_get();
    if (!state) { if (d[45] || d[46]) (void)r1_battery_task_flags_set(8); }
    else if (state==1 && !d[45] && !d[46]) (void)r1_native_charger_initialize();
    uint32_t charged=r1_battery_charged_state_refresh(state,b+36,b+12,b+40,b+14);
    if (charged && !read32(b+36)) {
        uint32_t tick=osKernelGetTickCount();write32(b+36,tick ? tick:1);
        uint16_t voltage=read16(d+42);write16(b+12,voltage);
        if (!read16(d+49)) write16(d+49,voltage);
        if (!d[48]) { uint8_t level=d[44];d[48]=level ? level:1; }
        r1_battery_charging_progress_reset();
    }
    int32_t sample=(int16_t)r1_battery_five_sample_filter_and_conversion();
    uint32_t offset=r1_batcfg_word1_signed_get();
    if (offset+299u<599u) sample=(int16_t)(uint16_t)((uint32_t)sample+offset);
    uint32_t stored=(uint32_t)sample;
    if (charged) {
        const union { uint32_t bits;float value; } scale={.bits=0x3f86c8b4};
        /* Keep conversion inside the native charged branch: speculating it
         * changes observable FPSCR flags even when no scaling is requested. */
        volatile uint32_t unsigned_sample=(uint32_t)sample;
        stored=(uint32_t)((float)unsigned_sample/scale.value);
    }
    write16(d+18+(uint32_t)(d[0]>>4)*2,stored);
    d[0]=(uint8_t)((d[0]&15u)|((((d[0]>>4)+1u)&7u)<<4));
    __aeabi_memclr((void *)(d+2),16);d[0]&=0xf0u;
    r1_battery_voltage_average();r1_battery_stuck_charge_recovery(state,b+36);
    uint8_t level;
    uint32_t voltage=read16(d+42);
    uint8_t charging=d[45];
    uint32_t charge_start=read32(b+36);
    if (!charging) level=(uint8_t)r1_battery_discharge_curve(voltage,charge_start);
    else level=(uint8_t)r1_battery_charging_cadence(voltage,charge_start);
    d[34+d[1]]=level;d[1]=(uint8_t)((d[1]+1u)&7u);
    uint32_t average=r1_battery_level_average();
    if (!b[1] || state || !d[44] || average<=d[44] || average>=95u) d[44]=(uint8_t)(average ? average:1);
    r1_battery_diagnostic_cadence_step(b+5,read32(b+36),read16(b+12),read32(b+40),read16(b+14),state);
    r1_battery_low_escalation();
    if (state==1) (void)r1_proto_report_battery_status(d[44],1);else r1_shared_power_client_release(0);
    level=d[44];if (level!=b[0]) { b[0]=level;(void)r1_glasses_tag_frame_send(level,state==1); }
    level=d[44];return level ? level:1;
}
