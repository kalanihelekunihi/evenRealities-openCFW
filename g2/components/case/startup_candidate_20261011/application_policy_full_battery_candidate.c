/* SPDX-License-Identifier: MIT
 * Stock 0x080072bc-0x08007376 complete full-battery counter/standby branch.
 * R5 is task-local live context established at 0x08007200.
 */
#include <stdint.h>
extern void case_policy_flash_write(uint32_t address,uint32_t ticks,uint32_t length); /* 0x0800598c */
extern void case_policy_log(uint32_t message);
extern void case_init_pmic_read(uint32_t address,uint8_t *out,uint32_t count);
extern void case_init_power_set(uint32_t enabled);
extern void case_init_boost_set(uint32_t enabled);
extern void case_init_wake_mask(uint32_t mask);
extern void case_init_wake_config(uint32_t mode);
extern void case_init_wake_clock(void);

uint8_t case_policy_full_battery_step_72bc(volatile uint8_t *state,
                                           volatile uint8_t *left,
                                           volatile uint8_t *right,
                                           uint8_t r5)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(shared[0x3du]!=0u || state[0x10u]==0u || left[0x11u]==0u ||
       left[0x13u]!=0u || state[0x11u]==0u || right[0x0du]==0u ||
       right[0x0fu]!=0u)return 0u;
    uint16_t left_count=(uint16_t)(*(volatile uint16_t *)(void *)(state+0x38u)+1u);
    uint16_t right_count=(uint16_t)(*(volatile uint16_t *)(void *)(right+0x14u)+1u);
    *(volatile uint16_t *)(void *)(state+0x38u)=left_count;
    *(volatile uint16_t *)(void *)(right+0x14u)=right_count;
    uint8_t old=r5;
    r5=(uint8_t)(r5+1u);
    if(old!=5u)return r5;
    case_policy_flash_write(0x20000948u,0x3840u,4u);
    if(shared[7u]==0u){case_policy_log(0x0800761cu);case_policy_log(0x08007608u);}
    uint8_t scratch=0u;
    case_init_pmic_read(0x10u,&scratch,1u);
    case_init_pmic_read(0x11u,&scratch,1u);
    case_init_power_set(0u);case_init_boost_set(0u);
    case_init_wake_mask(0x2bu);case_init_wake_config(0x2028u);
    *(volatile uint32_t *)(uintptr_t)0x40007018u=0x1003fu;
    case_init_wake_clock();
    return r5;
}
