/* SPDX-License-Identifier: MIT
 * Stock idle-standby sequence at 0x0800726a through WFI 0x080072b0.
 * Product message and device reads retain typed lower contracts.
 */
#include <stdint.h>
extern void case_policy_log(uint32_t message); /* 0x08009170, product string source */
extern void case_init_pmic_read(uint32_t address,uint8_t *out,uint32_t count); /* 0x080035d4 */
extern void case_init_power_set(uint32_t enabled); /* 0x08002c8e */
extern void case_init_boost_set(uint32_t enabled); /* 0x08002c30 */
extern void case_init_wake_mask(uint32_t mask); /* 0x08005094 */
extern void case_init_wake_config(uint32_t mode); /* 0x080050a8 */
extern void case_init_wake_clock(void); /* 0x080050c4 */
void case_policy_standby_idle(void)
{
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
        case_policy_log(0x080075f0u);
        case_policy_log(0x08007608u);
    }
    uint8_t scratch=0u;
    case_init_pmic_read(0x10u,&scratch,1u);
    case_init_pmic_read(0x11u,&scratch,1u);
    case_init_power_set(0u);case_init_boost_set(0u);
    case_init_wake_mask(0x2bu);case_init_wake_config(0x2028u);
    *(volatile uint32_t *)(uintptr_t)0x40007018u=0x1003fu;
    case_init_wake_clock();
}
