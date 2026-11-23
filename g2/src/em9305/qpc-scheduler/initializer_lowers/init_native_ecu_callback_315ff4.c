#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x315ff4..0x3160d2: validate a connection update request held in
 * the shared report (((uintptr_t)&em9305_ram_8027e0 + 0x30u): interval +0xc, instant +0xe, latency +0x10,
 * window +0x12, timeout +0x14). The interval must be 1..500 with latency
 * below 500 and window below the interval, (latency+1)*interval must stay
 * at or below 500, the timeout must be 10..3200 and at least twice the
 * span scaled by the current interval (+266) * 1.25. Invalid requests end
 * the link with reason 0x73 when bit 5 of ((uintptr_t)&em9305_ram_805a6c + 0x1au) is set. Valid ones are
 * stored (+846..+852, +260, +382) and flag bit 29 of +636 is set unless
 * nothing changed. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);

void opencfw_em9305_ecu_callback_315ff4(uintptr_t record)
{
    volatile uint16_t *report=&em9305_ram_8027e0.u16_802810;
    uint32_t window=report[9];
    uint32_t latency=report[8];
    uint32_t interval=report[6];
    uint32_t timeout=report[10];
    uint32_t valid=0u;
    if(window<500u)
        valid=((uint16_t)(interval-1u)<500u)&(latency<500u);
    uint32_t span=(latency+1u)*interval;
    uint32_t timeout_us=timeout*10u;
    if((int32_t)span>=501) valid=0u;
    else valid&=((uint16_t)(timeout-0xc81u)>0xf388u)&(window<interval);
    uint32_t current=*(volatile uint16_t *)(record+266u);
    uint32_t scaled=current+(current>>2)+((current&3u)!=0u);
    if(timeout_us<((span*scaled)<<1)||valid==0u) {
        if(em9305_ram_805a6c.u8_805a86&0x20u)
            (void)opencfw_em9305_receive_terminate_325c08(record,0x73u);
        return;
    }
    volatile uint16_t *stored=(volatile uint16_t *)(record+846u);
    uint32_t changed=1u;
    if(interval==stored[0]&&window==stored[2]&&
       latency==*(volatile uint16_t *)(record+260u)&&
       timeout_us==*(volatile uint16_t *)(record+382u))
        changed=0u;
    uint32_t instant=report[7];
    stored[0]=(uint16_t)interval;
    *(volatile uint16_t *)(record+260u)=(uint16_t)latency;
    *(volatile uint16_t *)(record+382u)=(uint16_t)timeout_us;
    stored[2]=(uint16_t)window;
    stored[3]=(uint16_t)timeout;
    stored[1]=(uint16_t)instant;
    if(changed!=0u) *(volatile uint32_t *)(record+636u)|=1u<<29;
}
