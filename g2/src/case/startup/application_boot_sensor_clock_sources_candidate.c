/* SPDX-License-Identifier: MIT
 * CASE 0x08005474 / 0x0800549c clock source calculations.
 */
#include <stdint.h>
extern const uint32_t case_boot_clock_shift_table[8]; /* 0x0800d3e8 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
/* Stock 0x08005474 (case_shift_selected) */
uint32_t case_boot_sensor_clock_5474(void)
{
    uint32_t control=rd32(0x40021008u);
    uint32_t index=((control>>12)&7u)*4u;
    uint32_t shift=case_boot_clock_shift_table[index>>2]&31u;
    return rd32(0x20000124u)>>shift;
}
/* Stock 0x0800549C (case_derive_clock) */
uint32_t case_boot_sensor_clock_549c(void)
{
    uint32_t control=rd32(0x40021008u);
    uint32_t mode=(control>>3)&7u;
    const uint32_t source=0x00f42400u;
    if(mode==0u){
        uint32_t shift=(rd32(0x40021000u)>>11)&7u;
        return case_policy_sensor_divide(source,1u<<shift);
    }
    if(mode==1u)return source>>1;
    if(mode==3u)return 32000u;
    if(mode==4u)return 32768u;
    if(mode!=2u)return 0u;
    uint32_t pll=rd32(0x4002100cu);
    uint32_t first=((pll>>4)&7u)+1u;
    uint32_t numerator=(pll&3u)==3u?(control<<26):source;
    uint32_t value=case_policy_sensor_divide(numerator,first);
    value*=((pll>>8)&127u);
    return case_policy_sensor_divide(value,(pll>>29)+1u);
}
