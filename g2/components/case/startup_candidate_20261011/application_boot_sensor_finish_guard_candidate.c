/* SPDX-License-Identifier: MIT
 * CASE 0x080063ec synchronous sensor transfer and buffer copy.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
extern uint32_t case_boot_sensor_open_ready(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t); /* 0x8ec4 */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
uint32_t case_boot_sensor_finish_guard(uint32_t d,const uint8_t *buffer,uint32_t length,uint32_t timeout)
{
    if(rd32(d+140u)!=32u)return 2u;
    uint32_t output=(uint32_t)(uintptr_t)buffer;
    if(output==0u||length==0u)return 1u;
    uint32_t mode=rd32(d+8u),linked=rd32(d+16u);
    if(mode==0x1000u&&linked==0u&&(output&1u)!=0u)return 1u;
    wr32(d+144u,0u);wr32(d+140u,34u);wr32(d+108u,0u);
    uint32_t start=case_policy_adc_tick();
    wr16(d+92u,(uint16_t)length);wr16(d+94u,(uint16_t)length);
    uint16_t mask;
    if(mode==0x1000u)mask=linked!=0u?255u:511u;
    else if(mode==0u)mask=linked!=0u?127u:255u;
    else if(mode==0x10000000u)mask=linked!=0u?63u:127u;
    else mask=0u;
    wr16(d+96u,mask);
    uint32_t width=(mode==0x1000u&&linked==0u)?2u:1u;
    while(rd16(d+94u)!=0u){
        if(case_boot_sensor_open_ready(d,32u,0u,start,timeout)!=0u)return 3u;
        uint32_t value=rd32(rd32(d)+36u);
        if(width==1u){
            *(volatile uint8_t *)(uintptr_t)output=(uint8_t)(value&(uint8_t)mask);
        }else{
            *(volatile uint16_t *)(uintptr_t)output=(uint16_t)(value&mask);
        }
        output+=width;
        wr16(d+94u,(uint16_t)(rd16(d+94u)-1u));
    }
    wr32(d+140u,32u);
    return 0u;
}
