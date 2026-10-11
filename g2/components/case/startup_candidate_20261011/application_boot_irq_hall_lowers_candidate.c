/* SPDX-License-Identifier: MIT
 * CASE 0x08003848 hall IRQ LED policy and 0x08002a5c hall state read.
 */
#include <stdint.h>
extern void case_policy_led_left_clear(uint32_t value); /* 0x6b80 */
extern void case_policy_led_right_clear(uint32_t value); /* 0x6b98 */
static uint8_t rd8(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
uint32_t case_boot_irq_hall_state(void)
{return rd8(0x200000bbu);}
void case_boot_irq_hall_prepare(uint32_t mode)
{
    const uint32_t s=0x2000087cu;
    uint32_t left=rd8(s+17u),right=rd8(s+16u),value;
    if(left==0u||right==0u){
        if(mode==0u){
            if(left!=0u||right!=0u)return;
            value=rd8(s+1u);
        }else{
            uint32_t a=rd8(s+78u),b=rd8(s+50u);
            value=a<=b?a:b;
        }
    }else{
        uint32_t a=rd8(s+78u),b=rd8(s+50u);
        value=a<=b?a:b;
    }
    if(value<90u){
        case_policy_led_left_clear(1u);
        case_policy_led_right_clear(0u);
    }else{
        case_policy_led_right_clear(1u);
        case_policy_led_left_clear(0u);
    }
}
