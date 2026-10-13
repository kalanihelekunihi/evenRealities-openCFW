#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002a68 periodic external-power edge debounce.
 */
#include <stdint.h>
extern uint32_t case_init_pin_read(uint32_t,uint32_t); /* 0x4e94 */
extern uint32_t case_init_pmic_read(uint32_t,uint8_t *,uint32_t); /* 0x35d4 */
extern void case_init_boost_set(uint32_t); /* 0x2c30 */
void case_boot_periodic_power_update(void)
{
    uint8_t desired=case_init_pin_read(0x50000400u,32u)!=0u?0u:1u;
    uint8_t observed=0xffu;
    (void)case_init_pmic_read(21u,&observed,1u);
    observed&=1u;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *counter=(volatile uint8_t *)(uintptr_t)0x20000028u;
    if(observed!=desired && state[3u]!=observed){*counter=0u;return;}
    *counter=(uint8_t)(*counter+1u);
    if(*counter<3u)return;
    state[3u]=desired;
    case_init_boost_set(desired==0u);
    *counter=0u;
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
        (void)case_policy_log(CASE_STRING_ADDR(08002b04));
        (void)case_policy_log(CASE_STRING_ADDR(08002b3c));
    }
}
