/* SPDX-License-Identifier: MIT
 * CASE 0x08006240 sensor peripheral open sequence.
 */
#include <stdint.h>
extern void case_boot_sensor_open_initialize(uint32_t descriptor); /* 0x6308 */
extern uint32_t case_boot_sensor_open_validate(uint32_t descriptor); /* 0x8bd8 */
extern void case_boot_sensor_open_apply(uint32_t descriptor); /* 0x85b0 */
extern uint32_t case_boot_sensor_open_finish(uint32_t descriptor); /* 0x867c */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x08006240 (case_prepare_controller_context) */
uint32_t case_boot_sensor_open(uint32_t descriptor)
{
    if(descriptor==0u)return 1u;
    if(rd32(descriptor+136u)==0u){
        *(volatile uint8_t *)(uintptr_t)(descriptor+132u)=0u;
        case_boot_sensor_open_initialize(descriptor);
    }
    wr32(descriptor+136u,36u);
    uint32_t hw=rd32(descriptor);
    wr32(hw,rd32(hw)&~1u);
    if(case_boot_sensor_open_validate(descriptor)==1u)return 1u;
    if(rd32(descriptor+40u)!=0u)case_boot_sensor_open_apply(descriptor);
    hw=rd32(descriptor);
    wr32(hw+4u,rd32(hw+4u)&~0x4800u);
    hw=rd32(descriptor);
    wr32(hw+8u,rd32(hw+8u)&~0x2au);
    hw=rd32(descriptor);
    wr32(hw,rd32(hw)|1u);
    return case_boot_sensor_open_finish(descriptor);
}
