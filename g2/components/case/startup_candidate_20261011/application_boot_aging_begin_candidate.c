#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08001334 aging state reset and task signals.
 */
#include <stdint.h>
extern int32_t case_policy_event_signal(uint32_t,uint32_t); /* 0xaaf0 */
void case_boot_aging_begin(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x200000f4u;
    state[1u]=1u;
    state[6u]=1u;
    state[2u]=0u;
    state[3u]=0u;
    state[4u]=0u;
    *(volatile uint32_t *)(uintptr_t)0x20000100u=0u;
    state[5u]=0u;
    state[7u]=4u;
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
        (void)case_policy_log(CASE_STRING_ADDR(0800137c));
        (void)case_policy_log(CASE_STRING_ADDR(080013b0));
    }
    (void)case_policy_event_signal(*(volatile uint32_t *)(uintptr_t)0x200000d4u,5000u);
    (void)case_policy_event_signal(*(volatile uint32_t *)(uintptr_t)0x200000d8u,2000u);
}
