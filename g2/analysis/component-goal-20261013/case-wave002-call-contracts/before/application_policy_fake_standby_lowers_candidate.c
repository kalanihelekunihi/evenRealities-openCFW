#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native 0x08003a00 fake-standby state change and 0x080013b8 clear.
 */
#include <stdint.h>
extern void case_policy_task_cancel(uint32_t task); /* 0x0800aa00 */
extern void case_policy_log(uint32_t message);
void case_policy_fake_standby_set(uint32_t side)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    if(side!=0u){
        volatile uint8_t *left=state+0x20u;
        left[0x14u]=0u;
        *(volatile uint32_t *)(void *)(state+0x3cu)=0u;
        *(volatile uint32_t *)(void *)(state+0x48u)=0u;
        *(volatile uint16_t *)(void *)(state+0x38u)=0u;
        left[0x11u]=0u;state[0x12u]=1u;
    }else{
        volatile uint8_t *right=state+0x40u;
        right[0x10u]=0u;
        *(volatile uint32_t *)(void *)(state+0x58u)=0u;
        *(volatile uint32_t *)(void *)(state+0x64u)=0u;
        *(volatile uint16_t *)(void *)(right+0x14u)=0u;
        right[0x0du]=0u;state[0x13u]=1u;
    }
}
void case_policy_fake_standby_clear(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    state[0x17u]=0u;
    case_policy_task_cancel(*(volatile uint32_t *)(void *)(shared+0x2cu));
    case_policy_task_cancel(*(volatile uint32_t *)(void *)(shared+0x30u));
    case_policy_task_cancel(*(volatile uint32_t *)(void *)(shared+0x28u));
    shared[3u]=0u;
    if(shared[7u]==0u){case_policy_log(CASE_STRING_ADDR(080013f4));case_policy_log(CASE_STRING_ADDR(08001404));}
}
