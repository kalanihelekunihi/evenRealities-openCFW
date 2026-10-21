/* SPDX-License-Identifier: MIT
 * Native CASE 0x080066ac synchronous sensor transmit through the descriptor.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
extern uint32_t case_boot_sensor_open_ready(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t); /* 0x8ec4 */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}

uint32_t case_boot_sensor_transfer(uint32_t descriptor,const uint8_t *packet,
                                   uint32_t count,uint32_t timeout)
{
    if(rd32(descriptor+136u)!=32u)return 2u;
    uint32_t source=(uint32_t)(uintptr_t)packet;
    if(source==0u || count==0u)return 1u;
    uint32_t halfwords=rd32(descriptor+8u)==0x1000u && rd32(descriptor+16u)==0u;
    if(halfwords!=0u && (source&1u)!=0u)return 1u;
    wr32(descriptor+144u,0u);wr32(descriptor+136u,33u);
    uint32_t start=case_policy_adc_tick();
    wr16(descriptor+84u,(uint16_t)count);
    wr16(descriptor+86u,(uint16_t)count);
    while(rd16(descriptor+86u)!=0u){
        if(case_boot_sensor_open_ready(descriptor,128u,0u,start,timeout)!=0u)return 3u;
        uint32_t value;
        if(halfwords!=0u){value=*(const uint16_t *)(uintptr_t)source & 0x1ffu;source+=2u;}
        else{value=*(const uint8_t *)(uintptr_t)source;source+=1u;}
        wr32(rd32(descriptor)+40u,value);
        wr16(descriptor+86u,(uint16_t)(rd16(descriptor+86u)-1u));
    }
    if(case_boot_sensor_open_ready(descriptor,64u,0u,start,timeout)!=0u)return 3u;
    wr32(descriptor+136u,32u);
    return 0u;
}
