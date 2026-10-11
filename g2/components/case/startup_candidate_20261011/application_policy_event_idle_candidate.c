/* SPDX-License-Identifier: MIT
 * Stock 0x08007b2e-0x08007e90 shared event and idle-standby gate.
 * Native event bits and elapsed time are typed scheduler/clock contracts.
 */
#include <stdint.h>
extern uint32_t case_policy_event_peek(uint32_t task); /* 0x0800a816 */
extern void case_policy_event_clear(uint32_t task,uint32_t bits); /* 0x0800a7d2 */
extern void case_policy_event_signal(uint32_t task,uint32_t value); /* 0x0800aaf0 */
extern void case_policy_fake_standby_clear(void); /* 0x080013b8 */
extern void case_policy_elapsed(uint32_t *out); /* 0x0800a01e */
extern void case_policy_log(uint32_t message);
extern void case_init_pmic_read(uint32_t address,uint8_t *out,uint32_t count);
extern void case_init_power_set(uint32_t enabled);
extern void case_init_boost_set(uint32_t enabled);
extern void case_init_wake_mask(uint32_t mask);
extern void case_init_wake_config(uint32_t mode);
extern void case_init_wake_clock(void);

void case_policy_event_idle_7b2e(volatile uint8_t *state)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(shared[3u]==0u)return;
    uint32_t event=case_policy_event_peek(*(volatile uint32_t *)(void *)(shared+0x38u));
    if((event&2u)!=0u){
        case_policy_event_clear(*(volatile uint32_t *)(void *)(shared+0x38u),2u);
        case_policy_event_signal(*(volatile uint32_t *)(void *)(shared+0x10u),0x9c4u);
    }
    if((event&0x1000u)!=0u){
        case_policy_event_clear(*(volatile uint32_t *)(void *)(shared+0x38u),0x1000u);
        case_policy_fake_standby_clear();
    }
    if(state[1u]!=0u || state[3u]!=0u)return;
    uint32_t elapsed=0u;
    case_policy_elapsed(&elapsed);
    if(elapsed>=0xcb2u)return;
    if(shared[7u]==0u){case_policy_log(0x08007eecu);case_policy_log(0x08007f18u);}
    uint8_t scratch=0u;
    case_init_pmic_read(0x10u,&scratch,1u);case_init_pmic_read(0x11u,&scratch,1u);
    case_init_power_set(0u);case_init_boost_set(0u);
    case_init_wake_mask(0x2bu);case_init_wake_config(0x2020u);
    *(volatile uint32_t *)(uintptr_t)0x40007018u=0x1003fu;
    case_init_wake_clock();
}
