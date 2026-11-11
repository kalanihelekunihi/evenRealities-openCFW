#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"

extern volatile uint8_t r1_health_mode_byte,r1_health_module_status,r1_wear_adt_sleep_gate;
extern volatile uint8_t r1_wear_sleep_status,r1_wear_sleep_latch;
extern void __aeabi_memclr(void *,size_t);
extern void r1_wear_motion_statistics(uint32_t,void *);
extern void r1_wear_on_decision(void *),r1_wear_off_decision(void *);
extern uint32_t r1_event_service_0008b028(uint32_t,const void *,uint32_t);

__attribute__((section(".text.r1_state_byte_nonzero_96a40")))
uint32_t r1_state_byte_nonzero_96a40(uint32_t value)
{
    if (value) return 1;
    return 0;
}

__attribute__((section(".text.r1_wear_motion_topic_callback")))
void r1_wear_motion_topic_callback(uint32_t context,uint32_t payload,uint32_t length)
{
    (void)context;(void)length;
    if (!payload) return;
    if (read16((const volatile uint8_t *)(uintptr_t)(payload+180u))<10) return;
    uint32_t previous=r1_state_byte_nonzero_96a40(r1_health_mode_byte);
    uint32_t module=r1_health_module_status;
    if (!module) r1_health_mode_byte=0;
    else if (module==1) r1_health_mode_byte=2;
    else if (r1_wear_adt_sleep_gate==1) r1_health_mode_byte=0;
    else {
        uint8_t statistics[24];
        __aeabi_memclr(statistics,sizeof(statistics));
        r1_wear_motion_statistics(payload,statistics);
        if (r1_health_mode_byte) r1_wear_off_decision(statistics);
        else r1_wear_on_decision(statistics);
    }
    uint32_t current=r1_state_byte_nonzero_96a40(r1_health_mode_byte);
    uint8_t status=(uint8_t)current;
    if (current!=previous) (void)r1_event_service_0008b028(4,&status,1);
    if (r1_wear_sleep_status==1 && r1_health_mode_byte==2) r1_wear_sleep_latch=1;
}
