/* SPDX-License-Identifier: MIT
 * CASE 0x0800867c final sensor readiness sequence.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x08004eac */
extern uint32_t case_boot_sensor_open_ready(uint32_t descriptor,uint32_t mask,
    uint32_t expected,uint32_t start,uint32_t control); /* 0x08008ec4 */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x0800867C (case_wait_controller_channels) */
uint32_t case_boot_sensor_open_finish(uint32_t descriptor)
{
    wr32(descriptor+144u,0u);
    uint32_t start=case_policy_adc_tick();
    uint32_t hw=rd32(descriptor);
    if((rd32(hw)&8u)!=0u &&
       case_boot_sensor_open_ready(descriptor,0x200000u,0u,start,0x01ffffffu)!=0u)
        return 3u;
    hw=rd32(descriptor);
    if((rd32(hw)&4u)!=0u &&
       case_boot_sensor_open_ready(descriptor,0x400000u,0u,start,0x01ffffffu)!=0u)
        return 3u;
    wr32(descriptor+136u,32u);
    wr32(descriptor+140u,32u);
    wr32(descriptor+108u,0u);
    wr32(descriptor+112u,0u);
    *(volatile uint8_t *)(uintptr_t)(descriptor+132u)=0u;
    return 0u;
}
